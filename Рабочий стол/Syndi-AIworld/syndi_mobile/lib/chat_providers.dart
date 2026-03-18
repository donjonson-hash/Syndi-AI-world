// lib/providers/chat_providers.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

final chatMessagesProvider = StateProvider<List<Map<String, dynamic>>>((ref) => []);
