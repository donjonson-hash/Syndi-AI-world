import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/models/big_five.dart';
import '../../core/providers/app_providers.dart';
import '../../widgets/loading_widget.dart';
import '../home_screen.dart';

class BigFiveTestScreen extends ConsumerStatefulWidget {
  const BigFiveTestScreen({super.key});

  @override
  ConsumerState<BigFiveTestScreen> createState() => _BigFiveTestScreenState();
}

class _BigFiveTestScreenState extends ConsumerState<BigFiveTestScreen> {
  int _currentQuestion = 0;
  final Map<int, int> _answers = {};
  List<BigFiveQuestion> _questions = [];
  bool _isLoading = true;

  // Тестовые вопросы (на случай если API не отвечает)
  final List<BigFiveQuestion> _mockQuestions = [
    BigFiveQuestion(id: 1, text: 'Я люблю знакомиться с новыми людьми', trait: 'extraversion', isReversed: false),
    BigFiveQuestion(id: 2, text: 'Я часто переживаю из-за мелочей', trait: 'neuroticism', isReversed: false),
    BigFiveQuestion(id: 3, text: 'Я довожу дела до конца', trait: 'conscientiousness', isReversed: false),
    BigFiveQuestion(id: 4, text: 'Мне нравится искусство и красивые вещи', trait: 'openness', isReversed: false),
    BigFiveQuestion(id: 5, text: 'Я доверяю людям', trait: 'agreeableness', isReversed: false),
    BigFiveQuestion(id: 6, text: 'Я предпочитаю работать в одиночестве', trait: 'extraversion', isReversed: true),
    BigFiveQuestion(id: 7, text: 'Я легко выхожу из себя', trait: 'neuroticism', isReversed: false),
    BigFiveQuestion(id: 8, text: 'Я люблю порядок', trait: 'conscientiousness', isReversed: false),
    BigFiveQuestion(id: 9, text: 'Мне нравится пробовать новое', trait: 'openness', isReversed: false),
    BigFiveQuestion(id: 10, text: 'Я ставлю себя на место других', trait: 'agreeableness', isReversed: false),
    BigFiveQuestion(id: 11, text: 'Я - душа компании', trait: 'extraversion', isReversed: false),
    BigFiveQuestion(id: 12, text: 'Я часто чувствую тревогу', trait: 'neuroticism', isReversed: false),
    BigFiveQuestion(id: 13, text: 'Я выполняю свои обещания', trait: 'conscientiousness', isReversed: false),
    BigFiveQuestion(id: 14, text: 'Мне нравится фантазировать', trait: 'openness', isReversed: false),
    BigFiveQuestion(id: 15, text: 'Я избегаю конфликтов', trait: 'agreeableness', isReversed: false),
  ];

  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    setState(() => _isLoading = true);
    
    try {
      final api = ref.read(apiClientProvider);
      final questions = await api.getQuestions();
      setState(() {
        _questions = questions;
        _isLoading = false;
      });
    } catch (e) {
      // Если API не доступен, используем мок-данные
      setState(() {
        _questions = _mockQuestions;
        _isLoading = false;
      });
    }
  }

  void _answerQuestion(int score) {
    setState(() {
      _answers[_questions[_currentQuestion].id] = score;
      
      if (_currentQuestion < _questions.length - 1) {
        _currentQuestion++;
      } else {
        _submitTest();
      }
    });
  }

  Future<void> _submitTest() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const LoadingWidget(message: 'Анализируем ваши ответы...'),
    );

    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getInt('user_id') ?? 1; // Временный ID
      
      final api = ref.read(apiClientProvider);
      final profile = await api.submitTest(_answers, userId);
      
      // Сохраняем результаты
      ref.read(userProvider.notifier).state = profile;
      await prefs.setBool('has_completed_test', true);
      
      if (context.mounted) {
        Navigator.pop(context); // Закрываем загрузку
        _showResults(profile.bigFive!);
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context); // Закрываем загрузку
        _showMockResults();
      }
    }
  }

  void _showResults(BigFiveProfile profile) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Ваш профиль готов!'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Ваш тип: ${profile.getPersonalityType()}',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.purple,
              ),
            ),
            const SizedBox(height: 16),
            _buildTraitBar('Открытость', profile.openness, Colors.blue),
            _buildTraitBar('Добросовестность', profile.conscientiousness, Colors.green),
            _buildTraitBar('Экстраверсия', profile.extraversion, Colors.orange),
            _buildTraitBar('Доброжелательность', profile.agreeableness, Colors.pink),
            _buildTraitBar('Нейротизм', profile.neuroticism, Colors.red),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const HomeScreen()),
              );
            },
            child: const Text('На главную'),
          ),
        ],
      ),
    );
  }

  void _showMockResults() {
    final mockProfile = BigFiveProfile(
      openness: 0.8,
      conscientiousness: 0.6,
      extraversion: 0.4,
      agreeableness: 0.7,
      neuroticism: 0.3,
    );
    _showResults(mockProfile);
  }

  Widget _buildTraitBar(String trait, double value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(trait, style: const TextStyle(fontSize: 12)),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: value,
                backgroundColor: Colors.grey[800],
                valueColor: AlwaysStoppedAnimation<Color>(color),
                minHeight: 8,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text('${(value * 100).toInt()}%'),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: LoadingWidget(message: 'Загружаем вопросы...'),
      );
    }

    final question = _questions[_currentQuestion];
    final progress = (_currentQuestion + 1) / _questions.length;

    return Scaffold(
      appBar: AppBar(
        title: Text('Вопрос ${_currentQuestion + 1} из ${_questions.length}'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.black,
              Colors.purple.withOpacity(0.1),
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.grey[800],
                valueColor: const AlwaysStoppedAnimation<Color>(Colors.purple),
              ),
              const SizedBox(height: 40),
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.grey[900],
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.purple.withOpacity(0.3)),
                ),
                child: Text(
                  question.text,
                  style: const TextStyle(
                    fontSize: 20,
                    height: 1.5,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: 40),
              const Text(
                'Насколько вы согласны?',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              _buildAnswerButton('Полностью не согласен', 1),
              const SizedBox(height: 12),
              _buildAnswerButton('Скорее не согласен', 2),
              const SizedBox(height: 12),
              _buildAnswerButton('Нейтрально', 3),
              const SizedBox(height: 12),
              _buildAnswerButton('Скорее согласен', 4),
              const SizedBox(height: 12),
              _buildAnswerButton('Полностью согласен', 5),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnswerButton(String text, int score) {
    return ElevatedButton(
      onPressed: () => _answerQuestion(score),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.grey[900],
        foregroundColor: Colors.white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: _answers.containsKey(_questions[_currentQuestion].id) && 
                   _answers[_questions[_currentQuestion].id] == score
                ? Colors.purple
                : Colors.grey[800]!,
          ),
        ),
      ),
      child: Text(
        text,
        style: const TextStyle(fontSize: 16),
      ),
    );
  }
}
