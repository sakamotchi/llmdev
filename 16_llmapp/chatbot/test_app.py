import pytest
from flask import session
from chatbot.app import app
from chatbot.graph import memory, get_messages_list

USER_MESSAGE_1 = "1たす2は？"
USER_MESSAGE_2 = "東京駅のイベントの検索結果を教えて"

@pytest.fixture
def client():
    """
    Flaskテストクライアントを作成
    """
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'your_secret_key'  # セッションのための秘密鍵
    client = app.test_client()
    with client.session_transaction() as session:
        session.clear()  # セッションをクリア
    yield client

def test_index_get_request(client):
    """
    GETリクエストで初期画面が正しく表示されるかをテスト
    """
    with client as c:
        response = c.get('/')
        assert response.status_code == 200, "GETリクエストが成功する必要があります。"
        assert b'<form' in response.data, "初期画面にフォームが含まれている必要があります。"
        assert memory.storage == {}, "メモリは初期化されている必要があります。"

def test_index_post_request(client):
    """
    POSTリクエストでボットの応答が正しく返されるかをテスト
    """
    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is None, "初期状態ではセッションにthread_idが設定されていないはずです。"

    response = client.post('/', data={'user_message': USER_MESSAGE_1})
    assert response.status_code == 200, "POSTリクエストが成功する必要があります。"
    decoded_data = response.data.decode('utf-8')
    assert '1たす2は？' in decoded_data, "ユーザーのメッセージが応答に含まれている必要があります。"
    assert '3' in decoded_data, "ボットの応答に計算結果が含まれている必要があります。"

    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is not None, "POSTリクエスト後にセッションにthread_idが設定されている必要があります。"

def test_memory_persistence_with_session(client):
    """
    複数のPOSTリクエストでメモリがセッションごとに保存されるかをテスト
    """
    client.post('/', data={'user_message': USER_MESSAGE_1})
    client.post('/', data={'user_message': USER_MESSAGE_2})

    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is not None, "セッションにthread_idが設定されている必要があります。"

    messages = get_messages_list(memory, thread_id)

    assert len(messages) >= 2, "メモリには2つ以上のメッセージが保存されている必要があります。"
    assert any("1たす2" in msg['text'] for msg in messages if msg['class'] == 'user-message'), "ユーザーの入力がメモリに保存されている必要があります。"
    assert any("東京駅" in msg['text'] for msg in messages if msg['class'] == 'user-message'), "複数のメッセージが正しく保存される必要があります。"

def test_clear_endpoint(client):
    """
    /clearエンドポイントがセッションとメモリを正しくリセットするかをテスト
    """
    client.post('/', data={'user_message': USER_MESSAGE_1})

    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is not None, "セッションにthread_idが設定されている必要があります。"

    response = client.post('/clear')
    assert response.status_code == 200, "POSTリクエストが成功する必要があります。"
    assert b"<form" in response.data, "初期画面にフォームが含まれている必要があります。"

    with client.session_transaction() as session:
        thread_id = session.get('thread_id')
        assert thread_id is None, "セッションからthread_idが削除されている必要があります。"
    
    # メモリがクリアされていることを確認
    cleared_messages = memory.get({"configurable": {"thread_id": thread_id}})
    assert cleared_messages is None, "メモリはクリアされている必要があります。"

def test_template_rendering(client):
    """
    テンプレートが正しくレンダリングされるかをテスト
    """
    user_message = "1たす2は？"

    with client as c:
        response = c.post('/', data={'user_message': user_message})
        decoded_data = response.data.decode('utf-8')

        assert response.status_code == 200, "POSTリクエストが成功する必要があります。"
        assert '1たす2は？' in decoded_data, "ユーザーのメッセージが応答に含まれている必要があります。"
        assert '3' in decoded_data, "ボットの応答に計算結果が含まれている必要があります。"