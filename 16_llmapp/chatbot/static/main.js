window.onload = function() {
    // チャットボックスを取得
    const chatBox = document.getElementById('chat-box');

    // チャットボックスのスクロールを一番下に設定
    chatBox.scrollTop = chatBox.scrollHeight;

    // Ctrl + Enterで送信
    const form = document.getElementById('chat-form');
    const textarea = document.getElementById('user-input');

    textarea.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault(); // デフォルトの動作をキャンセル
            form.submit(); // フォームを送信
        }
    }
    );
}