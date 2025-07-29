css = '''
<style>
    .chat-message {
        padding: 8px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user {
        background-color: #DCF8C6;
        text-align: right;
    }
    .bot {
        background-color: #F1F0F0;
        text-align: left;
    }
</style>
'''

user_template = '''
<div class="chat-message user">
    <strong>You:</strong> {{MSG}}
</div>
'''

bot_template = '''
<div class="chat-message bot">
    <strong>Bot:</strong> {{MSG}}
</div>
'''
