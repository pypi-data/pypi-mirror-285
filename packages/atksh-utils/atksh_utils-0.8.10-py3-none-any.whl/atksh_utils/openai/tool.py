import io
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.parse
from code import InteractiveConsole
from concurrent.futures import ThreadPoolExecutor as TPE
from contextlib import redirect_stderr, redirect_stdout
from functools import partial
from threading import Lock, Semaphore
from typing import List

import backoff
import pypdf
import requests
import urllib3
from bs4 import BeautifulSoup as bs4
from duckduckgo_search import DDGS
from urllib3.exceptions import InsecureRequestWarning, ReadTimeoutError

from .prompt import (
    SEARCH_RESULT_SUMMARIZE_PROMPT,
    SUBTASK_PROMPT,
    TLANSATE_PROMPT,
    VISIT_PAGE_SUMMARIZE_PROMPT,
)
from .token import clean_text, count_token, sub_tokenize

urllib3.disable_warnings(InsecureRequestWarning)

# Create a temporary directory for storing files to $HOME/.cache/askgpt/ or OPENAI_TOOLS_PYTHON_CACHE_DIR
CACHE_DIR = os.getenv(
    "OPENAI_TOOLS_PYTHON_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".cache", "askgpt")
)
os.makedirs(CACHE_DIR, exist_ok=True)
SESSION_PATH = os.path.join(CACHE_DIR, "session.pkl")

Print_LOCK = Lock()
DDGS_LOCK = Lock()
API_LOCK = Semaphore(16)
Python_LOCK = Lock()
Console_LOCK = Lock()
Shell_LOCK = Lock()
UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
PYTHON_PATH = sys.executable


CONSOLE = InteractiveConsole(locals=None)
MAX_ATTEMPTS = 5
MAX_SEARCH_RESULTS = 100
ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
ARXIV_REGEX = re.compile(
    r"arxiv\.org\/(?:abs|pdf)\/((?:[0-9]+\.[0-9]+)|(?:old\.\d+)|(?:[a-z]+\/\\d+))(?:v\d+)?",
    re.UNICODE,
)


def make_chunk(text: str, max_length: int, overlap_ratio: float = 0.2) -> list[str]:
    text = clean_text(text)
    length = count_token(text)
    i = 0
    while True:
        try:
            (s, t), ret = sub_tokenize(text, i, i + max_length)
        except:
            break
        yield ret
        if t == length:
            break
        prev_i = i
        i += max_length
        diff = i - t
        i -= diff
        delta = prev_i - i
        i -= int(delta * overlap_ratio)
        i = min(i, length)
        if i == length:
            break


@backoff.on_exception(
    partial(backoff.expo, base=3, factor=2),
    (requests.exceptions.RequestException, ReadTimeoutError),
    max_tries=5,
    jitter=backoff.full_jitter,
)
def get_response(url: str) -> requests.Response:
    return requests.get(
        url,
        headers={"User-Agent": UserAgent, "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"},
        timeout=15,
        verify=False,
    )


def extract_output_if_possible(text: str) -> str:
    groups = re.findall(r"<output(\d+)>(.*?)</output(\1)>", text, re.DOTALL)
    if len(groups) == 0:
        return text
    out = []
    for _, t, _ in groups:
        out.append(t.strip())
    return "\n\n".join(out)


def verbose():
    return os.getenv("ASKGPT_VERBOSE", "0") == "1"


def random_sleep():
    for _ in range(3):
        time.sleep(random.uniform(0.1, 1.0))


def parse_args(arguments: str) -> dict:
    try:
        return json.loads(arguments)
    except json.decoder.JSONDecodeError:
        try:
            return json.loads(arguments, strict=False)
        except:
            return arguments


def cb(chunk, _):
    with Print_LOCK:
        light_cyan = "\033[96m"
        reset = "\033[0m"
        if (finish_reason := chunk.choices[0].dict().get("finish_reason")) is not None:
            if finish_reason == "stop":
                print("\n")
        token = chunk.choices[0].delta.content
        if token:
            print(f"{light_cyan}{token}{reset}", end="")


def get_answer_subtask_function(ai: "OpenAI"):
    subtask_model_name = ai.model_name

    def answer_subtask(
        context_description: str,
        subtask_description: str,
        output_format: str,
        subtask_argments_for_each_subtask: List[str],
    ) -> str:
        """Answers the subtask of the main task described by the parent AI. Given the context and the subtask, provide each solution for each subtask_argments_for_each_subtask. Every text should be instruction for AI. After calling this function, you will get the solutions for each subtask_argments_for_each_subtask. So, you must generate the unifined text from the solutions. Don't wait for this calling.

        :param context_description: The context description, which is the important information to solve the subtask.
        :type context_description: str
        :param subtask_description: The subtask description, which is the specific task to solve. This takes an argument from subtask_argments_for_each_subtask. So, the subtask is done in parallel.
        :type subtask_description: str
        :param output_format: The output format of the subtask.
        :type output_format: str
        :param subtask_argments_for_each_subtask: The list of arguments for each subtask. Each argument is a string.
        :type subtask_argments_for_each_subtask: list[str]
        :return: The solutions for each subtask_argments_for_each_subtask. You must generate the unified text from the solutions.
        :rtype: list[str]
        """
        subtask_child = ai.make_child(subtask_model_name, temperature=0.2, top_p=0.8, use_func=True)
        subtask_child.set_system_prompt(SUBTASK_PROMPT)
        prompts = []
        for arg in subtask_argments_for_each_subtask:
            prompt = f"""
            ## Context Description
            {context_description}
            ## Subtask Description
            {subtask_description}

            ## Subtask Argument
            subtask_argument: {arg}

            ## Output Format
            {output_format}

            Now, answer the subtask with the given context and subtask description.
            """.strip()
            prompt = "\n".join([line.strip() for line in prompt.split("\n") if line.strip()])
            prompts.append(prompt)

        def call(prompt):
            try:
                with API_LOCK:
                    ms, _ = subtask_child(
                        prompt,
                        stream_callback=cb if verbose() else None,
                    )
            except:
                return f"Error: {traceback.format_exc()}.\nPlease try again or try another subtask."
            with API_LOCK:
                return subtask_child.try_call(
                    "Write the solution for the subtask with the given output format.",
                    stream_callback=cb if verbose() else None,
                    messages=ms,
                )[1]

        futures = []
        with TPE(max_workers=len(prompts)) as executor:
            for prompt in prompts:
                future = executor.submit(call, prompt)
                futures.append(future)
            rets = [future.result() for future in futures]
        output = []
        for arg, ret in zip(subtask_argments_for_each_subtask, rets):
            output.append(f"### Subtask Argument: {arg}\n\n### Output\n{ret}".strip())
        return "\n\n".join(output).strip()

    return answer_subtask


def get_translate_function(ai: "OpenAI"):
    tl_model_name = ai.model_name if "4o" not in ai.model_name else "gpt-4o-mini"
    tl_max_context_length = 5000
    tl_max_context_length -= count_token(TLANSATE_PROMPT)

    def translate(text: str, target_lang: str) -> str:
        """Translates the text into the target language.

        :param text: The text to translate.
        :type text: str
        :param target_lang: The target language. For example, `ja` for Japanese.
        :type target_lang: str
        :return: The translated text.
        :rtype: str
        """
        text = clean_text(text)
        text = text.strip()
        if len(text) > tl_max_context_length:
            return f"Error: The text is too long. Please split the text into multiple texts each of which is less than {tl_max_context_length} tokens."
        translate_child = ai.make_child(tl_model_name, temperature=0.2, top_p=0.8)
        translate_child.set_system_prompt(TLANSATE_PROMPT)
        error = "Unknown error."
        for i in range(MAX_ATTEMPTS):
            for _ in range(i + 1):
                random_sleep()
            try:
                with API_LOCK:
                    return translate_child(
                        f"Text: {text}\nTarget Language: {target_lang}\nTranslation: ",
                        stream_callback=cb if verbose() else None,
                    )[1]
            except:
                error = traceback.format_exc()
                print(error)
                continue
        return f"Error: {error}.\nPlease try again or try another text."

    return translate


def get_browser_functions(ai: "OpenAI"):
    visit_page_model_name = ai.model_name if "4o" not in ai.model_name else "gpt-4o-mini"
    visit_page_max_context_length = 100000 if "gpt-4o" in visit_page_model_name else 10000
    visit_page_max_context_length -= count_token(VISIT_PAGE_SUMMARIZE_PROMPT)

    def _search_summarize(query_text: str, results: str) -> str:
        """Summarizes the query text and results."""
        search_result_child = ai.make_child(ai.model_name, temperature=0.4, top_p=0.95)
        search_result_child.set_system_prompt(SEARCH_RESULT_SUMMARIZE_PROMPT)
        error = "Unknown error."
        for i in range(MAX_ATTEMPTS):
            for _ in range(i + 1):
                random_sleep()
            try:
                with API_LOCK:
                    return extract_output_if_possible(
                        search_result_child(
                            f"Query: {query_text}\nResults: {results}\nSummary: ",
                            stream_callback=cb if verbose() else None,
                        )[1]
                    )
            except:
                error = traceback.format_exc()
                print(error)
                continue
        return f"Error: {error}.\nPlease try again or try another query."

    def _page_summarize(query_text: str, page: str) -> str:
        """Summarizes the query text and page."""
        visit_page_child = ai.make_child(visit_page_model_name, temperature=0.4, top_p=0.95)
        visit_page_child.set_system_prompt(VISIT_PAGE_SUMMARIZE_PROMPT)
        error = "Unknown error."
        for i in range(MAX_ATTEMPTS):
            for _ in range(i + 1):
                random_sleep()
            try:
                text = f"Query: {query_text}\nPage: {page}\nSummary: "
                with API_LOCK:
                    return extract_output_if_possible(
                        visit_page_child(
                            text,
                            stream_callback=cb if verbose() else None,
                        )[1]
                    )
            except:
                error = traceback.format_exc()
                print(error)
                continue
        return f"Error: {error}.\nPlease try again or try another url or wait_sec for a while."

    def quick_search(query_words: List[str]) -> str:
        """Searche with the given query words and summarize the searched results. The query words must be a list of strings and each length must be less than 10 tokens. **EACH WORD MUST NOT INCLUDE ANY SPECIAL CHARACTERS LIKE `\n`, `\\n`, `\u3000` and so on. If you encounter a rate limit error, please wait for a while and try again.**

        :param query_words: The query words. For example, `["Apple", "iPhone", "12", "日本", "発売日"]`. Each word must be a string and each length must be less than 10 tokens.
        :type query_words: list[str]
        :return: summarized search results.
        :rtype: str
        """
        search_query = " ".join(query_words).strip()
        print(f"Search query: {search_query}")
        your_query = repr(search_query)[1:-1]
        attempts = 0
        search_results = []
        while attempts < MAX_ATTEMPTS:
            with DDGS_LOCK:
                with DDGS() as ddgs:
                    search_results = ddgs.text(
                        search_query,
                        region="ja-ja",
                        safesearch="Off",
                        max_results=MAX_SEARCH_RESULTS,
                        backend="html",
                    )
                    search_results = list(search_results)
                    if search_results:
                        break
                    time.sleep(1.5 + attempts)
                    random_sleep()
                attempts += 1
                if verbose():
                    print(f"[quick_search] Retrying {attempts}...")

        results = json.dumps(search_results, ensure_ascii=False, indent=2)
        ret = "Error: No results found.\nPlease try again or try another query."
        if results:
            ret = f"Your query: {your_query}\n\nSummarized Search Results:\n"
            ret += _search_summarize(search_query, results).strip()
            ret += "\nPlease visit all the five pages so that you can get correct infomation to answer by `visit_page` tool."
        return ret

    def visit_page(summarization_points_of_view: str, url: str) -> str:
        """Visit the page and summarize the page with respect to the summarization points of view argument.

        :param summarization_points_of_view: The summarization points of view.
        :type summarization_points_of_view: str
        :param url: The url to visit (must be a valid url like `https://www.google.com`).
        :type url: str
        :return: The summarized text of the page.
        :rtype: str
        """
        your_query = repr(summarization_points_of_view)[1:-1]
        if "arxiv.org" in url:
            paper_id = ARXIV_REGEX.search(url).group(1)
            url = f"https://www.arxiv-vanity.com/papers/{paper_id}/"
        try:
            random_sleep()
            response = get_response(url)
            content_type = response.headers.get("Content-Type", "")

            text: str = ""
            if "application/pdf" in content_type:
                # PDFファイルの処理
                pdf_content = response.content
                with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
                    temp_pdf.write(pdf_content)
                    temp_pdf.seek(0)
                    reader = pypdf.PdfReader(temp_pdf.name)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            else:
                # 通常のHTMLページの処理
                soup = bs4(response.text, "html.parser")
                body = soup.find("body").text.strip()
                links = []
                for a in soup.find_all("a"):
                    href = a.get("href")
                    if href is None:
                        continue
                    n = a.text.strip()
                    if len(n) < 2:
                        continue
                    href = urllib.parse.urljoin(url, href)
                    links.append(f"{n}: `{href}`")
                links = " - " + "\n - ".join(links)
                text += body + "\n====LINKS====\n" + links

            while True:
                rets = []
                with TPE(max_workers=8) as executor:
                    futures = []
                    for chunk in make_chunk(text, visit_page_max_context_length):
                        future = executor.submit(
                            _page_summarize, summarization_points_of_view, chunk
                        )
                        futures.append(future)
                    for future in futures:
                        ret = future.result()
                        rets.append(ret)
                text = "\n".join(rets).strip()
                if len(text) < visit_page_max_context_length:
                    break
            ret = text
            ret = ret.strip()
            ret += '\nPlease visit "Related Links" if available so that you can get correct infomation to answer by `visit_page` tool.'
            ret = f"Your query: {your_query}\n\nSummarized Page:\n{ret}"
        except:
            e = traceback.format_exc()
            print(e)
            ret = f"Error: {e}.\nPlease try again or try another url."
        return ret

    return quick_search, visit_page


def run_pyhton_with_session_locally(code: str) -> str:
    """This is a function that executes Python code and returns the stdout. Don't forget to print the result. In this environment, you have the capability to run external network functionalities since it is a local environment, not sandboxed.

    :param code: Python code of multiple lines. You must print the result. For example, `value = 2 + 3; print(value)`.
    :type code: str
    :return: stdout of running the Python code.
    :rtype: str
    """
    lines = code.split("\n")
    lines = ["    " + line for line in lines]
    code = "\n".join(lines)
    result = ""
    with Python_LOCK, io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
        out = None
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as f:
            try:
                f.write("import traceback\n")
                f.write("import dill\n")
                f.write(f"try:\n    dill.load_session('{SESSION_PATH}')\nexcept:\n    pass\n")
                f.write("\n\n\n")
                f.write("try:\n")
                f.write(code)
                f.write(
                    "\nexcept:\n    print(f'ERROR: {traceback.format_exc()}')\n    print('\\n\\n\\n')\n"
                )
                f.write("else:\n    print('\\n\\n\\nThe code is executed successfully.')\n")
                f.write("    print('The following is the system message about session.')\n")
                f.write(
                    f"\ntry:\n    dill.dump_session('{SESSION_PATH}')\nexcept:"
                    "\n    print('[SYSTEM INFO]: Failed to save this session:', traceback.format_exc())\n"
                    "else:\n    print('[SYSTEM INFO]: Saved this session.')\n"
                )
                f.flush()
                out = subprocess.check_output(f"{PYTHON_PATH} {f.name}", shell=True, text=True)
            except:
                e = traceback.format_exc()
                print(e)
                result += f"Error: {e}.\nPlease try again.\n"
            if out == "":
                result += "NotPrintedError('The result is not printed.')\nPlease print the result in your code."
            elif out is not None:
                result += out
            result += ANSI_ESCAPE.sub("", buf.getvalue())
            result = result.strip()
    if verbose():
        print("=== Run Python Code ===")
        print(result)
        print(
            "Note: If you plot graphs, the user did see them. Don't ask the user to run the code locally."
        )
        print("=======================")
    return result


def bash(command: str) -> str:
    """Execute the given command and return the result.

    :param command: The command to execute. For example, `ls -l`.
    :type command: str
    :return: The result of the execution of the command.
    :rtype: str
    """
    with Shell_LOCK:
        try:
            ret = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            return_code = e.returncode
            output = e.output
            ret = f"Error: return_code={return_code}, output={output}"
        except:
            e = traceback.format_exc()
            print(e)
            ret = f"Error: {e}.\nPlease try again or try another command."
    ret = ANSI_ESCAPE.sub("", str(ret)).strip()
    if verbose():
        print("=== Bash ===")
        print(ret)
        print("============")
    return ret


def pip_install(command: str) -> str:
    """Install the given package with pip and return the result. Use this if and only if you encounter an error with `import`.

    :param command: The packages to install. For example, `numpy pandas`.
    :type command: str
    :return: The result of the installation of the package.
    :rtype: str
    """
    with Shell_LOCK:
        try:
            ret = subprocess.check_output(f"{PYTHON_PATH} -m pip install {command}", shell=True)
        except subprocess.CalledProcessError as e:
            return_code = e.returncode
            output = e.output
            ret = f"Error: return_code={return_code}, output={output}"
        except:
            e = traceback.format_exc()
            print(e)
            ret = f"Error: {e}.\nPlease try again or try another command."
    ret = ANSI_ESCAPE.sub("", str(ret)).strip()
    if verbose():
        print("=== Pip Install ===")
        print(ret)
        print("===================")
    return ret


def clear_all_python_session() -> bool:
    """Clears the exec_python_code session.

    :return: True if the session is cleared successfully.
    :rtype: bool
    """
    try:
        if os.path.exists(SESSION_PATH):
            os.remove(SESSION_PATH)
        return True
    except:
        return False


def wait_sec(seconds: int = 1) -> str:
    """Wait for the given seconds(1 second by default). This is useful when you want to write a too long text. 1 secons enables you to write about 4096 tokens. So before reaching the limit, you can use this function to wait for a while.

    :param seconds: The seconds to wait.
    :type seconds: int, optional
    :return: waited message.
    :rtype: str
    """
    time.sleep(seconds)
    return "Waited for {} seconds.".format(seconds)
