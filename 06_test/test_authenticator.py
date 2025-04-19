from authenticator import Authenticator
import pytest

@pytest.fixture
def authenticator():
    return Authenticator()

# registerメソッドでユーザーが登録できることを確認するテスト
def test_register(authenticator):
    authenticator.register("testuser", "password123")
    assert "testuser" in authenticator.users
    assert authenticator.users["testuser"] == "password123"
# registerメソッドで同じユーザー名で登録しようとするとエラーが発生することを確認するテスト
def test_register_duplicate(authenticator):
    authenticator.register("testuser", "password123")
    with pytest.raises(ValueError, match="エラー: ユーザーは既に存在します。"):
        authenticator.register("testuser", "newpassword")
# loginメソッドで正しいユーザー名とパスワードでログインできることを確認するテスト
def test_login_success(authenticator):
    authenticator.register("testuser", "password123")
    result = authenticator.login("testuser", "password123")
    assert result == "ログイン成功"
# loginメソッドで間違ったパスワードでログインしようとするとエラーが発生することを確認するテスト
def test_login_wrong_password(authenticator):
    authenticator.register("testuser", "password123")
    with pytest.raises(ValueError, match="エラー: ユーザー名またはパスワードが正しくありません。"):
        authenticator.login("testuser", "wrongpassword")