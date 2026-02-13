import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/plant_list_item.dart';

class PlantApiService {
  PlantApiService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  static const String _envBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  String get _baseUrl {
    if (_envBaseUrl.isNotEmpty) {
      return _envBaseUrl;
    }
    if (kIsWeb) {
      return 'http://localhost:8080';
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      // Android emulator reaches host loopback via 10.0.2.2.
      return 'http://10.0.2.2:8080';
    }
    // iOS simulator (and desktop) can use localhost directly.
    return 'http://localhost:8080';
  }

  Future<List<PlantListItem>> fetchPlantsBySeason({
    required String seasonCode,
    required int month,
    String regionCode = 'IN-KA',
  }) async {
    final uri = Uri.parse('$_baseUrl/api/v1/plants/by-season').replace(
      queryParameters: {
        'season': seasonCode,
        'month': '$month',
        'region_code': regionCode,
        'limit': '20',
      },
    );

    final response = await _client.get(uri);
    if (response.statusCode != 200) {
      throw Exception('Failed to load plants (${response.statusCode})');
    }

    final payload = jsonDecode(response.body) as Map<String, dynamic>;
    final data = payload['data'] as List<dynamic>? ?? const [];
    return data
        .map((item) => PlantListItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
