# atksh-utils

This is my collection of utilities.


## Installation

```bash
$ pip install atksh-utils
```

### askgpt command

You can use the `askgpt` command to ask questions to GPT-4.


#### Examples

```bash
$ export OPENAI_API_KEY="YOUR_API_KEY"

$ askgpt
Continue the conversation. To send your reply, please press Enter more than three times.
>>> 以下の式を解け:
>>> - 1 + 1/2 + 1/4 + ...
>>> - x + y = 4, pi * x - e^y = 0.24
>>>
>>> pythonを使っても良い
>>>
>>>
>>>

AI: Thinking...

了解しました。あなたの質問に最善を尽くして答えます。まず、与えられた2つの問題を解決するためのプランを説明します。

1. 数列の和の問題:
   - 与えられた数列は無限等比数列です: 1 + 1/2 + 1/4 + ...
   - 無限等比数列の和の公式を使用して、この数列の和を求めます。
   - 公式は S = a / (1 - r) です。ここで、a は最初の項であり、r は公比です。

2. 連立方程式の問題:
   - 与えられた連立方程式は次の通りです: x + y = 4, pi * x - e^y = 0.24
   - この連立方程式を解くために、数値解析の手法を使用するか、代数的に解を求めます。
   - Pythonの数値計算ライブラリを利用して、この連立方程式の数値解を見つけることができます。

これらの問題を解決するために、Pythonのコードを実行することにします。それでは、まずは数列の和の問題から取り組みます。その後、連立方程式の問題に移ります。無限等比数列 1 + 1/2 + 1/4 + ... の和は 2 です。

次に、連立方程式 x + y = 4, pi * x - e^y = 0.24 を解くために Python を使用します。これは数値解析の問題であり、Python の数値計算ライブラリを用いて解を求めることができます。それでは、Python コードを実行して解を見つけましょう。連立方程式 x + y = 4, pi * x - e^y = 0.24 の解は、x ≈ 2.1338 と y ≈ 1.8662 です。

以上で、与えられた2つの問題の解答を完了しました。最初の無限等比数列の和は 2 であり、二つ目の連立方程式の解は x ≈ 2.1338、y ≈ 1.8662 です。

Continue the conversation. To send your reply, please press Enter more than three times.
>>> ^D

Bye!
$ askgpt --disable-gpt4
>>> 明日の東京の天気は？
>>>
>>>
>>>

AI: Thinking...

明日の東京の天気は曇時々晴で、最高気温は21℃から23℃、最低気温は14℃から6℃となる見込みです。降水確率は10％で、一部では雨や雷雨がありそうです。体調に注意が必要です。また、明け方までは雨や雷雨がありそうです。最高気温は22度前後で、寒暖差で体調を崩さないようにしてください。

Continue the conversation. To send your reply, please press Enter more than three times.
>>> どうやってその情報を得ましたか？
>>>
>>>
>>>

AI: Thinking...

私は、あなたの質問に対する最適な回答を提供するために、functions.quick_searchツールを使用して明日の東京の天気に関する情報を検索しました。その結果、複数の天気予報サイトから明日の天気に関する情報を取得し、それを元に回答を提供しました。

Continue the conversation. To send your reply, please press Enter more than three times.
>>>
>>>
>>>
>>>
Do you want to quit? (y/n): y

Bye!
$ askgpt -h
usage: askgpt [-h] [--disable-gpt4] [--verbose]

options:
  -h, --help      show this help message and exit
  --disable-gpt4  Disable GPT-4.
  --verbose       Verbose mode.
```


## Development

To install this for development, run the following commands in your terminal:

```bash
python -m pip install -e '.[dev]'
pre-commit install
```

## OpenAI

```python
ai = OpenAI(key, "gpt-4o")

print(ai("Just answer the value of (5243 + 642) x (5314 - 4231) // 100"))
# The value of the expression (5243 + 642) x (5314 - 4231) // 100 is 7112.


def mul(a: int, b: int) -> int:
    """This is a multiplication function.

    :param a: An integer.
    :type a: int
    :param b: An integer.
    :type b: int
    :return: The sum of a and b.
    :rtype: int
    """
    return a * b


def add(a: int, b: int) -> int:
    """This is an addition function.

    :param a: An integer.
    :type a: int
    :param b: An integer.
    :type b: int
    :return: The sum of a and b.
    :rtype: int
    """
    return a + b


def sub(a: int, b: int) -> int:
    """This is a subtraction function.

    :param a: An integer.
    :type a: int
    :param b: An integer.
    :type b: int
    :return: The sum of a and b.
    :rtype: int
    """
    return a - b


def div(a: int, b: int) -> int:
    """This is a division function.

    :param a: An integer.
    :type a: int
    :param b: An integer.
    :type b: int
    :return: The sum of a and b.
    :rtype: int
    """
    return a // b

ai.set_function(mul)
ai.set_function(add)
ai.set_function(sub)
ai.set_function(div)

print(ai("Just answer the value of (5243 + 642) x (5314 - 4231) // 100")[1])
# The value of (5243 + 642) x (5314 - 4231) // 100 is 63734.


ai = OpenAI(key, "gpt-4o")
ai.set_browser_functions()
print(ai("How the weather in Tokyo?")[1])
# The current weather in Tokyo varies depending on the source. According to AccuWeather, it is partly sunny with a temperature of 89°F. BBC Weather predicts thundery showers tonight with a low temperature of 22°C. Timeanddate.com reports an overcast sky with a temperature of 82°F. The Weather Network and The Weather Channel provide forecasts for the next 7 and 13 days respectively. Weather Underground also offers weather conditions for Tokyo and other cities.
```
