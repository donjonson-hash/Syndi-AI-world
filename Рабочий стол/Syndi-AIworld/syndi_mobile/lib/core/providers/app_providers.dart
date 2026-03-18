import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/syndi_api_client.dart';
import '../models/user.dart';

// API Client Provider
final apiClientProvider = Provider<SyndiApiClient>((ref) {
  return SyndiApiClient();
});

// User Provider
final userProvider = StateProvider<UserProfile?>((ref) => null);

// Loading Provider
final loadingProvider = StateProvider<bool>((ref) => false);

// Chat Messages Provider
final chatMessagesProvider = StateNotifierProvider<ChatMessagesNotifier, List<ChatMessage>>((ref) {
  return ChatMessagesNotifier();
});

class ChatMessage {
  final String id;
  final String text;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.text,
    required this.isUser,
    required this.timestamp,
  });
}

class ChatMessagesNotifier extends StateNotifier<List<ChatMessage>> {
  ChatMessagesNotifier() : super([]);

  void addMessage(ChatMessage message) {
    state = [...state, message];
  }

  void clearMessages() {
    state = [];
  }
}
