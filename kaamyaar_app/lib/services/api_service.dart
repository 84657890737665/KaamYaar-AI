
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl =
      'https://kaamyaar-ai-xr3b5px5sq-el.a.run.app';

  // ─── CORE AGENTIC FLOW ────────────────────────────────────────────

  /// Agent 1: Parse raw text in any language
  static Future<Map<String, dynamic>> parseRequest({
    required String rawText,
    String languageHint = 'auto',
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/parse-request'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'raw_text': rawText, 'language_hint': languageHint}),
    );
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('parse-request failed: ${res.statusCode} ${res.body}');
  }

  /// Agent 2: Find providers
  static Future<List<dynamic>> findProviders({
    required String serviceType,
    required String location,
    double? budget,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/find-providers'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'service_type': serviceType,
        'location': location,
        'budget': budget ?? 2000,
      }),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      return data['providers'] ?? [];
    }
    throw Exception('find-providers failed: ${res.statusCode} ${res.body}');
  }

  /// Agent 3: Rank providers
  static Future<List<dynamic>> rankProviders({
    required List<dynamic> providers,
    required String serviceType,
    required String location,
    double? budget,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/rank-providers'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'providers': providers,
        'service_type': serviceType,
        'location': location,
        'budget': budget ?? 2000,
      }),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      return data['ranked_providers'] ?? providers;
    }
    return providers;
  }

  /// Agent 4: Calculate price
  static Future<Map<String, dynamic>> calculatePrice({
    required String providerId,
    required String serviceType,
    required double distanceKm,
    double? budget,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/calculate-price'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'provider_id': providerId,
        'service_type': serviceType,
        'distance_km': distanceKm,
        'budget': budget ?? 2000,
      }),
    );
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('calculate-price failed: ${res.statusCode}');
  }

  /// Agent 5: Create booking
  static Future<Map<String, dynamic>> createBooking({
    required String providerId,
    required String serviceType,
    required String location,
    required String scheduledTime,
    required double budget,
    String? userId,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/create-booking'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'provider_id': providerId,
        'service_type': serviceType,
        'location': location,
        'scheduled_time': scheduledTime,
        'budget': budget,
        'user_id': userId ?? 'guest_user',
      }),
    );
    if (res.statusCode == 200 || res.statusCode == 201) {
      return jsonDecode(res.body);
    }
    throw Exception('create-booking failed: ${res.statusCode} ${res.body}');
  }

  // ─── MOBILE API ───────────────────────────────────────────────────

  static Future<Map<String, dynamic>> parseVoice({
    required String audioText,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/mobile/parse-voice'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'audio_text': audioText}),
    );
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('parse-voice failed: ${res.statusCode}');
  }

  static Future<List<dynamic>> getNearbyProviders({
    required double lat,
    required double lng,
    String? serviceType,
    double radiusKm = 10,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/mobile/nearby-providers'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'latitude': lat,
        'longitude': lng,
        'service_type': serviceType,
        'radius_km': radiusKm,
      }),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      return data['providers'] ?? [];
    }
    throw Exception('nearby-providers failed: ${res.statusCode}');
  }

  static Future<Map<String, dynamic>> bookService({
    required String providerId,
    required String serviceType,
    required String location,
    required String scheduledTime,
    required double budget,
    String? userId,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/mobile/book-service'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'provider_id': providerId,
        'service_type': serviceType,
        'location': location,
        'scheduled_time': scheduledTime,
        'budget': budget,
        'user_id': userId ?? 'guest_user',
      }),
    );
    if (res.statusCode == 200 || res.statusCode == 201) {
      return jsonDecode(res.body);
    }
    throw Exception('book-service failed: ${res.statusCode}');
  }

  static Future<Map<String, dynamic>> getBookingStatus(
      String bookingId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/api/v1/mobile/booking-status/$bookingId'),
    );
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('booking-status failed: ${res.statusCode}');
  }

  // ─── QUALITY ──────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> submitFeedback({
    required String bookingId,
    required int rating,
    String? comment,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/quality/submit-feedback'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'booking_id': bookingId,
        'rating': rating,
        'comment': comment ?? '',
      }),
    );
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('submit-feedback failed: ${res.statusCode}');
  }

  // ─── SAFETY ───────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> getSafetyStatus(
      String bookingId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/api/v1/safety/status/$bookingId'),
    );
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception('safety-status failed: ${res.statusCode}');
  }

  static Future<Map<String, dynamic>> createEmergencyAlert({
    required String bookingId,
    required String alertType,
    required String location,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/safety/emergency-alert'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'booking_id': bookingId,
        'alert_type': alertType,
        'location': location,
      }),
    );
    if (res.statusCode == 200 || res.statusCode == 201) {
      return jsonDecode(res.body);
    }
    throw Exception('emergency-alert failed: ${res.statusCode}');
  }

  // ─── DISPUTES ─────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> fileDispute({
    required String bookingId,
    required String reason,
    String? description,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/v1/disputes/file-dispute'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'booking_id': bookingId,
        'reason': reason,
        'description': description ?? '',
      }),
    );
    if (res.statusCode == 200 || res.statusCode == 201) {
      return jsonDecode(res.body);
    }
    throw Exception('file-dispute failed: ${res.statusCode}');
  }

  // ─── HEALTH CHECK ─────────────────────────────────────────────────

  static Future<bool> healthCheck() async {
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}