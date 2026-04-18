import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/big_five.dart';
import '../models/chat.dart';

// Base URL for the Syndi backend API
const String baseUrl = 'https://dev.syndi.ai/api'; // или http://localhost:8000/api

/// Response model for login endpoint.
class LoginResponse {
  final String token;
  final int userId;
  final String name;

  LoginResponse({
    required this.token,
    required this.userId,
    required this.name,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      token: json['access_token'] as String,
      userId: json['user_id'] as int,
      name: json['name'] as String,
    );
  }

  /// Mock response for development/testing purposes.
  factory LoginResponse.mock(String email) {
    return LoginResponse(
      token: 'mock_jwt_token_${DateTime.now().millisecondsSinceEpoch}',
      userId: 1,
      name: email.split('@').first,
    );
  }
}

/// Singleton API client for all Syndi backend communication.
/// Use via Riverpod [apiClientProvider] — do not instantiate directly.
class SyndiApiClient {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  SyndiApiClient() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Attach JWT token if available
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('auth_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        // ignore: avoid_print
        print('API Error [${error.response?.statusCode}]: ${error.message}');
        return handler.next(error);
      },
    ));
  }

  // ==================== AUTH ====================

  /// Authenticate user with email and password.
  /// Returns [LoginResponse] with JWT token and basic user info.
  /// Falls back to a mock response when the backend is unreachable.
  Future<LoginResponse> login(String email, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      final loginResponse = LoginResponse.fromJson(response.data as Map<String, dynamic>);
      // Persist token for subsequent requests
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', loginResponse.token);
      await prefs.setInt('user_id', loginResponse.userId);
      await prefs.setString('user_name', loginResponse.name);
      return loginResponse;
    } catch (_) {
      // Mock fallback — remove once backend is live
      final mock = LoginResponse.mock(email);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', mock.token);
      await prefs.setInt('user_id', mock.userId);
      await prefs.setString('user_name', mock.name);
      return mock;
    }
  }

  // ==================== USER PROFILE ====================

  /// Fetch the authenticated user's profile.
  /// Falls back to a mock [UserProfile] when the backend is unreachable.
  Future<UserProfile> getUserProfile() async {
    try {
      final response = await _dio.get('/users/me');
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      // Mock fallback
      return UserProfile(
        id: 1,
        name: 'Demo User',
        email: 'demo@syndi.ai',
        createdAt: DateTime(2026, 3, 1),
      );
    }
  }

  // ==================== CHAT ====================

  /// Send a chat message to Kristina AI agent.
  /// Returns a [ChatMessage] with the agent's reply.
  /// Falls back to an echo mock when the backend is unreachable.
  Future<ChatMessage> sendChatMessage(String text) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getInt('user_id') ?? 1;
      final response = await _dio.post('/agents/1/chat', data: {
        'message': text,
        'user_id': userId,
      });
      final chatResponse = ChatResponse.fromJson(response.data as Map<String, dynamic>);
      return ChatMessage.agent(chatResponse.message);
    } catch (_) {
      // Mock fallback — echo reply from Kristina
      return ChatMessage.agent('Kristina (mock): я получила твоё сообщение — "$text"');
    }
  }

  // ==================== BIG FIVE TEST ====================

  /// Fetch Big Five test questions from the backend.
  Future<List<BigFiveQuestion>> getQuestions() async {
    try {
      final response = await _dio.get('/test/questions');
      return (response.data as List)
          .map((q) => BigFiveQuestion.fromJson(q as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('Failed to load questions: $e');
    }
  }

  /// Submit Big Five answers and receive the computed [UserProfile].
  Future<UserProfile> submitTest(Map<String, int> answers, int userId) async {
    try {
      final response = await _dio.post('/test/submit', data: {
        'user_id': userId,
        'answers': answers,
      });
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Failed to submit test: $e');
    }
  }

  // ==================== USERS ====================

  /// Create a new user account.
  Future<UserProfile> createUser(String name, String email) async {
    try {
      final response = await _dio.post('/users', data: {
        'name': name,
        'email': email,
      });
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Failed to create user: $e');
    }
  }

  /// Fetch a user by ID.
  Future<UserProfile> getUser(int userId) async {
    try {
      final response = await _dio.get('/users/$userId');
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw Exception('Failed to get user: $e');
    }
  }

  // ==================== MATCHING ====================

  /// Fetch Smart Match results for the given user.
  Future<List<Match>> getMatches(int userId) async {
    try {
      final response = await _dio.get('/matches/$userId');
      return (response.data as List)
          .map((m) => Match.fromJson(m as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw Exception('Failed to get matches: $e');
    }
  }
}
