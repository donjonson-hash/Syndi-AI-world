import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/syndi_api_client.dart';
import '../models/user.dart';
import '../models/chat.dart';

// ---------------------------------------------------------------------------
// API Client — single instance shared across the app
// ---------------------------------------------------------------------------

/// Provides the singleton [SyndiApiClient].
/// All screens and notifiers must consume API calls through this provider.
final apiClientProvider = Provider<SyndiApiClient>((ref) {
  return SyndiApiClient();
});

// ---------------------------------------------------------------------------
// User state
// ---------------------------------------------------------------------------

/// Holds the currently authenticated [UserProfile], or null if not logged in.
final userProvider = StateProvider<UserProfile?>((ref) => null);

// ---------------------------------------------------------------------------
// Loading indicator
// ---------------------------------------------------------------------------

/// Global loading state used by screens that lack a local loading flag.
final loadingProvider = StateProvider<bool>((ref) => false);

// ---------------------------------------------------------------------------
// Chat messages
// ---------------------------------------------------------------------------

/// Provides and manages the list of chat messages for the Kristina chat screen.
/// Use [apiClientProvider] inside this notifier to call [SyndiApiClient.sendChatMessage].
final chatMessagesProvider =
    StateNotifierProvider<ChatMessagesNotifier, List<ChatMessage>>((ref) {
  return ChatMessagesNotifier(ref.read(apiClientProvider));
});

/// Manages the chat message list and API communication for the chat screen.
class ChatMessagesNotifier extends StateNotifier<List<ChatMessage>> {
  final SyndiApiClient _api;

  ChatMessagesNotifier(this._api) : super([]);

  /// Adds a user message and fetches the agent reply via [SyndiApiClient.sendChatMessage].
  Future<void> sendMessage(String text) async {
    // Optimistically add the user message
    state = [...state, ChatMessage.user(text)];

    try {
      final reply = await _api.sendChatMessage(text);
      state = [...state, reply];
    } catch (e) {
      state = [
        ...state,
        ChatMessage.agent('Ошибка: не удалось получить ответ от Kristina.'),
      ];
    }
  }

  /// Clears all messages in the current conversation.
  void clearMessages() {
    state = [];
  }
}
