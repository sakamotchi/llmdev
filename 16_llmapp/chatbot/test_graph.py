import pytest
from langchain_openai import OpenAIEmbeddings
from chatbot.graph import (
    get_bot_response,
    get_messages_list,
    memory,
    build_graph,
    define_tools,
    create_index,
    )

# モック用のテストデータ
USER_MESSAGE_1 = "1たす2は？"
USER_MESSAGE_2 = "東京駅のイベントの検索結果を教えて"
USER_MESSAGE_3 = "有給休暇の日数は？"
THREAD_ID = "test_thread"

@pytest.fixture
def setup_memory():
    """
    テスト用に新しいメモリを初期化。
    """
    memory.storage.clear()
    return memory

@pytest.fixture
def setup_graph():
    """
    テスト用に新しいグラフを構築。
    """
    return build_graph("gpt-4o-mini", memory)

def test_define_tools():
    """
    define_tools関数が正しくツールを定義できるかをテスト。
    """
    tools = define_tools()
    assert len(tools) > 0, "ツールが正しく定義されている必要があります。"
    assert any(tool.name == "retriever_company_rules" for tool in tools), "retriever_company_rulesツールが定義されている必要があります。"

def test_create_index():
    """
    create_index関数が正しくインデックスを作成できるかをテスト。
    """
    persist_directory = "./test_chroma_db"
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    try:
        index = create_index(persist_directory, embedding_model)
        assert index is not None, "インデックスが正しく作成されている必要があります。"
    except Exception as e:
        pytest.fail(f"インデックスの作成に失敗しました: {e}")

def test_get_bot_response_single_message(setup_memory):
    """
    ボットがシンプルなメッセージに応答できるかをテスト。
    """
    response = get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)
    assert isinstance(response, str), "応答は文字列である必要があります。"
    assert "3" in response, "1たす2の計算結果が正しく応答されるべきです。"

def test_get_bot_response_with_rag(setup_memory):
    """
    ボットがRetrieverベースの質問応答を正しく処理できるかをテスト。
    """
    response = get_bot_response(USER_MESSAGE_3, setup_memory, THREAD_ID)
    assert isinstance(response, str), "応答は文字列である必要があります。"
    assert "有給休暇" in response, "有給休暇に関する情報が正しく応答されるべきです。"

def test_get_bot_response_multiple_messages(setup_memory):
    """
    ボットが複数のメッセージに応答できるかをテスト。
    """
    get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)
    get_bot_response(USER_MESSAGE_2, setup_memory, THREAD_ID)
    messages = get_messages_list(setup_memory, THREAD_ID)
    assert len (messages) >= 2, "メッセージ履歴に少なくとも2つのエントリが含まれている必要があります。"
    assert any("1たす2" in msg['text'] for msg in messages if msg['class'] == 'user-message'), "ユーザーの入力が履歴に含まれる必要があります。"
    assert any("東京駅" in msg['text'] for msg in messages if msg['class'] == 'user-message'), "複数のメッセージが正しく保存される必要があります。"

def test_memory_clear_on_new_session(setup_memory):
    """
    新しいセッションが開始されたときにメモリがクリアされるかをテスト。
    """
    get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)

    # メモリの状態を確認
    initial_messages = get_messages_list(setup_memory, THREAD_ID)
    assert len(initial_messages) > 0, "初期メッセージがメモリに保存されている必要があります。"

    # メモリをクリア
    setup_memory.storage.clear()

    # 再度メッセージリストを取得し、メモリが空になっていることを確認
    cleared_messages = setup_memory.get({"configurable": {"thread_id": THREAD_ID}})

    # 再度メッセージリストを取得し、メモリが空になっていることを確認
    assert cleared_messages is None or 'channel_values' not in cleared_messages, "メモリはクリアされている必要があります。"

def test_build_graph(setup_memory):
    """
    グラフが正しく構築され、応答を生成できるかをテスト
    """
    graph = build_graph("gpt-4o-mini", setup_memory)
    response = graph.invoke(
        {"messages": [("user", USER_MESSAGE_1)]},
        {"configurable": {"thread_id": THREAD_ID}},
        stream_mode="values"
    )
    assert response["messages"][-1].content, "グラフが有効な応答を生成する必要があります。"

def test_get_messages_list(setup_memory):
    """
    メモリ内のメッセージリストが正しく取得できるかをテスト
    """
    get_bot_response(USER_MESSAGE_1, setup_memory, THREAD_ID)
    messages = get_messages_list(setup_memory, THREAD_ID)
    assert len(messages) > 0, "応答後、メッセージリストが空であってはなりません。"
    assert any(isinstance(msg, dict) for msg in messages), "メッセージリストは辞書のリストである必要があります。"
    assert any(msg['class'] == 'user-message' for msg in messages), "メッセージリストにユーザーのメッセージが含まれている必要があります。"
    assert any(msg['class'] == 'bot-message' for msg in messages), "メッセージリストにボットのメッセージが含まれている必要があります。"

# 実行用
if __name__ == "__main__":
    pytest.main()