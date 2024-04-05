from openai import OpenAI
import json  # JSON文字列を解析したり、PythonオブジェクトをJSON形式に変換する関数を提供
import streamlit as st

client = OpenAI()


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
# unitにはデフォルト値として"fahrenheit"が設定
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)  # weather_info辞書をJSON文字列に変換して返す


def run_conversation():
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
    # GPTモデルが呼び出すことができるget_current_weather関数を記述する辞書を含むリストを定義
    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]
    # clientオブジェクトのchat.completions.createメソッドを呼び出し、モデル識別子、メッセージ、関数を指定し、function_callを"auto"に設定して呼び出します。
    # これにより、会話がGPTモデルに送信され、オプションでget_current_weather関数を呼び出すことができます。レスポンスはresponse変数に割り当てられます。
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    # Streamlitを使用して、Webアプリケーションに"first response"というテキストを書き込む
    st.write("first response")
    # デバッグまたは検査の目的で、レスポンスオブジェクト全体をWebアプリケーションに書き込みます
    st.write(response)
    # レスポンスオブジェクトから最初の選択肢のメッセージ部分を抽出します。これには、GPTモデルの返信または関数呼び出しリクエストが含まれます。
    response_message = response.choices[0].message

    # Step 2: check if GPT wanted to call a function
    # response_messageがfunction_call属性を持っているか、そしてそれがNoneまたはFalseでないかを確認
    if hasattr(response_message, "function_call") and response_message.function_call:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        # 関数名と実際のPython関数オブジェクトをマッピングする辞書を定義
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        # 呼び出す関数の名前を抽出します。
        function_name = response_message.function_call.name

        fuction_to_call = available_functions[function_name]
        # 関数呼び出しのためのJSONエンコードされた引数を解析
        function_args = json.loads(response_message.function_call.arguments)
        # パースされた引数で要求された関数を呼び出し、その結果をfunction_responseに割り当てる
        function_response = fuction_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )
        # Webアプリケーションに"python function output"というテキストを書き込む
        st.write("python function output")
        # 呼び出された関数の出力をWebアプリケーションに書き込む
        st.write(function_response)

        # Step 4: send the info on the function call and function response to GPT
        # オリジナルのresponse_messageをmessagesリストに追加し、会話を拡張します。
        messages.append(response_message)
        # 関数応答の役割、名前、および内容を含む新しいメッセージをmessagesリストに追加します。
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        st.write("second request messages")
        # 更新されたmessagesリストをWebアプリケーションに書き込みます。
        st.write(messages)
        # 関数応答を含む更新されたメッセージでGPTモデルに新しいリクエストを送信し、レスポンスをsecond_responseに割り当てます。
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response


st.title("function calling")

clicked = st.button(label="Run Conversation")

if clicked:
    result = run_conversation()
    st.write("final answer")
    st.write(result)
