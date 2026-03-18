import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/user.dart';
import '../../core/providers/app_providers.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  String _userName = '';

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _userName = prefs.getString('user_name') ?? 'Пользователь';
    });
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    
    if (context.mounted) {
      Navigator.pushReplacementNamed(context, '/');
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(userProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Профиль'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Аватар
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.purple, Colors.blue],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 3),
              ),
              child: const Center(
                child: Text(
                  '👤',
                  style: TextStyle(fontSize: 50),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              _userName,
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Присоединился в марте 2026',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[400],
              ),
            ),
            const SizedBox(height: 32),

            // Психологический профиль
            if (user?.bigFive != null) ...[
              const Divider(color: Colors.grey),
              const SizedBox(height: 16),
              const Text(
                'Ваш психологический профиль',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              _buildProfileCard(user!.bigFive!),
            ],

            const SizedBox(height: 24),
            _buildStatCard(
              icon: Icons.people_outline,
              title: 'Найдено партнёров',
              value: '3',
              color: Colors.green,
            ),
            const SizedBox(height: 12),
            _buildStatCard(
              icon: Icons.chat_outlined,
              title: 'Диалогов с Kristina',
              value: '12',
              color: Colors.purple,
            ),
            const SizedBox(height: 12),
            _buildStatCard(
              icon: Icons.emoji_events_outlined,
              title: 'Завершено тестов',
              value: '2',
              color: Colors.orange,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileCard(BigFiveProfile profile) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildTraitRow('Открытость', profile.openness, Colors.blue),
            const SizedBox(height: 12),
            _buildTraitRow('Добросовестность', profile.conscientiousness, Colors.green),
            const SizedBox(height: 12),
            _buildTraitRow('Экстраверсия', profile.extraversion, Colors.orange),
            const SizedBox(height: 12),
            _buildTraitRow('Доброжелательность', profile.agreeableness, Colors.pink),
            const SizedBox(height: 12),
            _buildTraitRow('Нейротизм', profile.neuroticism, Colors.red),
          ],
        ),
      ),
    );
  }

  Widget _buildTraitRow(String trait, double value, Color color) {
    return Row(
      children: [
        SizedBox(
          width: 120,
          child: Text(
            trait,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
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
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[400],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    value,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
