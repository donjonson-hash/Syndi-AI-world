import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'home_screen.dart';
import 'test/big_five_test_screen.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkUserStatus();
  }

  Future<void> _checkUserStatus() async {
    await Future.delayed(const Duration(seconds: 2)); // Показываем сплэш 2 секунды
    
    final prefs = await SharedPreferences.getInstance();
    final hasCompletedTest = prefs.getBool('has_completed_test') ?? false;
    final userId = prefs.getInt('user_id');

    if (mounted) {
      if (userId != null) {
        if (hasCompletedTest) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const HomeScreen()),
          );
        } else {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const BigFiveTestScreen()),
          );
        }
      } else {
        // Новый пользователь - показываем экран приветствия
        _showWelcomeScreen();
      }
    }
  }

  void _showWelcomeScreen() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Добро пожаловать в Syndi!'),
        content: const Text(
          'Давай познакомимся. Как тебя зовут?',
          style: TextStyle(fontSize: 16),
        ),
        actions: [
          TextField(
            decoration: const InputDecoration(
              hintText: 'Введите имя',
              border: OutlineInputBorder(),
            ),
            onSubmitted: (name) async {
              if (name.isNotEmpty) {
                final prefs = await SharedPreferences.getInstance();
                await prefs.setString('user_name', name);
                if (context.mounted) {
                  Navigator.pop(context);
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => const BigFiveTestScreen()),
                  );
                }
              }
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Colors.purple.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.auto_awesome,
                size: 60,
                color: Colors.purple,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'SYNDI AI',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                letterSpacing: 4,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Найди своих людей',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
            ),
          ],
        ),
      ),
    );
  }
}
