import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/plant_list_item.dart';

class PlantApiService {
  PlantApiService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8080',
  );

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
