import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/big_five.dart';
import '../models/chat.dart';

class SyndiApiClient {
  static const String baseUrl = 'http://localhost:8000'; // Замените на ваш сервер
  
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
        // Добавляем токен авторизации если есть
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('auth_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        print('API Error: ${error.message}');
        return handler.next(error);
      },
    ));
  }

  // ==================== BIG FIVE TEST ====================
  
  Future<List<BigFiveQuestion>> getQuestions() async {
    try {
      final response = await _dio.get('/test/questions');
      return (response.data as List)
          .map((q) => BigFiveQuestion.fromJson(q))
          .toList();
    } catch (e) {
      throw Exception('Failed to load questions: $e');
    }
  }

  Future<UserProfile> submitTest(Map<String, int> answers, int userId) async {
    try {
      final response = await _dio.post('/test/submit', data: {
        'user_id': userId,
        'answers': answers,
      });
      return UserProfile.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to submit test: $e');
    }
  }

  // ==================== USERS ====================
  
  Future<UserProfile> createUser(String name, String email) async {
    try {
      final response = await _dio.post('/users', data: {
        'name': name,
        'email': email,
      });
      return UserProfile.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create user: $e');
    }
  }

  Future<UserProfile> getUser(int userId) async {
    try {
      final response = await _dio.get('/users/$userId');
      return UserProfile.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to get user: $e');
    }
  }

  // ==================== CHAT WITH KRISTINA ====================
  
  Future<ChatResponse> chatWithKristina(String message, int userId) async {
    try {
      final response = await _dio.post('/agents/1/chat', data: {
        'message': message,
        'user_id': userId,
      });
      return ChatResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to chat: $e');
    }
  }

  // ==================== MATCHING ====================
  
  Future<List<Match>> getMatches(int userId) async {
    try {
      final response = await _dio.get('/matches/$userId');
      return (response.data as List)
          .map((m) => Match.fromJson(m))
          .toList();
    } catch (e) {
      throw Exception('Failed to get matches: $e');
    }
  }
}
