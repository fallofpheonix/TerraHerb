class PlantListItem {
  const PlantListItem({
    required this.id,
    required this.scientificName,
    required this.primaryCommonName,
    required this.plantType,
    required this.lifecycle,
    required this.inSeason,
    required this.suitabilityScore,
  });

  final int id;
  final String scientificName;
  final String primaryCommonName;
  final String plantType;
  final String lifecycle;
  final bool inSeason;
  final double suitabilityScore;

  factory PlantListItem.fromJson(Map<String, dynamic> json) {
    return PlantListItem(
      id: json['id'] as int,
      scientificName: (json['scientific_name'] ?? '') as String,
      primaryCommonName: (json['primary_common_name'] ?? '') as String,
      plantType: (json['plant_type'] ?? '') as String,
      lifecycle: (json['lifecycle'] ?? '') as String,
      inSeason: (json['in_season'] ?? false) as bool,
      suitabilityScore: (json['suitability_score'] as num?)?.toDouble() ?? 0,
    );
  }
}
