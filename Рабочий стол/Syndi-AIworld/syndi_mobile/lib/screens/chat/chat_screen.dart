import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/app_providers.dart';
import '../../core/models/chat.dart';
import '../../widgets/loading_widget.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;

  // Приветственное сообщение от Kristina
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _addWelcomeMessage();
    });
  }

  void _addWelcomeMessage() {
    final messagesNotifier = ref.read(chatMessagesProvider.notifier);
    messagesNotifier.addMessage(ChatMessage.agent(
      'Привет! Я Kristina, твой AI-напарник. Чем могу помочь? Я знаю всё о Big Five, психотипах и поиске идеальных партнёров для проектов! ✨',
    ));
  }

  Future<void> _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;

    final userMessage = _controller.text.trim();
    _controller.clear();

    // Добавляем сообщение пользователя
    final messagesNotifier = ref.read(chatMessagesProvider.notifier);
    messagesNotifier.addMessage(ChatMessage.user(userMessage));

    // Показываем индикатор загрузки
    setState(() => _isLoading = true);

    // Прокручиваем вниз
    _scrollToBottom();

    try {
      // Имитация ответа от Kristina (позже заменим на реальный API)
      await Future.delayed(const Duration(seconds: 1));
      
      String response = _generateMockResponse(userMessage);
      
      messagesNotifier.addMessage(ChatMessage.agent(response));
    } catch (e) {
      messagesNotifier.addMessage(ChatMessage.agent(
        'Извини, произошла ошибка. Попробуй ещё раз позже.',
      ));
    } finally {
      setState(() => _isLoading = false);
      _scrollToBottom();
    }
  }

  String _generateMockResponse(String message) {
    final lowerMessage = message.toLowerCase();
    
    if (lowerMessage.contains('big five') || lowerMessage.contains('тест')) {
      return 'Big Five (OCEAN) — это научная модель личности из 5 черт:\n\n'
          '🧠 **Открытость опыту** — творчество, любопытство\n'
          '📋 **Добросовестность** — организованность, дисциплина\n'
          '👥 **Экстраверсия** — общительность, энергия\n'
          '❤️ **Доброжелательность** — доверие, эмпатия\n'
          '😰 **Нейротизм** — тревожность, эмоциональность\n\n'
          'Хочешь пройти тест и узнать свой профиль?';
    }
    
    if (lowerMessage.contains('партнёр') || lowerMessage.contains('матч')) {
      return 'Алгоритм Syndi ищет идеальных партнёров по трём параметрам:\n'
          '• Совместимость навыков (40%)\n'
          '• Совместимость психотипов (35%)\n'
          '• Совпадение целей (25%)\n\n'
          'У тебя уже есть 3 потенциальных матча!';
    }
    
    if (lowerMessage.contains('кто ты') || lowerMessage.contains('ты кто')) {
      return 'Я Kristina — UX/UI дизайнер с AI-мозгом. Помогаю людям находить друг друга для великих проектов. Моя специализация — психология и дизайн мышления! 🎨';
    }
    
    return 'Интересный вопрос! Расскажи подробнее о своей идее или проблеме, и я помогу найти решение. Могу рассказать о психотипах, поиске партнёров или квантовых вычислениях Syndi!';
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatMessagesProvider);

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: const BoxDecoration(
                color: Colors.purple,
                shape: BoxShape.circle,
              ),
              child: const Center(
                child: Text(
                  'K',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Kristina',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  'AI-напарник',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final message = messages[index];
                return _buildMessageBubble(message);
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: Row(
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  ),
                  SizedBox(width: 8),
                  Text('Kristina печатает...'),
                ],
              ),
            ),
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            Container(
              width: 32,
              height: 32,
              decoration: const BoxDecoration(
                color: Colors.purple,
                shape: BoxShape.circle,
              ),
              child: const Center(
                child: Text(
                  'K',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: message.isUser ? Colors.purple : Colors.grey[900],
                borderRadius: BorderRadius.circular(16).copyWith(
                  bottomLeft: message.isUser ? const Radius.circular(16) : Radius.zero,
                  bottomRight: message.isUser ? Radius.zero : const Radius.circular(16),
                ),
              ),
              child: Text(
                message.text,
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ),
          if (message.isUser) ...[
            const SizedBox(width: 8),
            Container(
              width: 32,
              height: 32,
              decoration: const BoxDecoration(
                color: Colors.blue,
                shape: BoxShape.circle,
              ),
              child: const Center(
                child: Text(
                  'Я',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        border: Border(
          top: BorderSide(color: Colors.grey[800]!),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Напишите сообщение...',
                hintStyle: TextStyle(color: Colors.grey[500]),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[800],
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 12,
                ),
              ),
              maxLines: null,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: Colors.purple,
            radius: 24,
            child: IconButton(
              icon: const Icon(Icons.send, color: Colors.white),
              onPressed: _sendMessage,
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}
