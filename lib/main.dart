import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'data/models/plant_list_item.dart';
import 'data/services/plant_api_service.dart';

void main() {
  runApp(const TerraHerbariumApp());
}

class TerraHerbariumApp extends StatelessWidget {
  const TerraHerbariumApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Terra Herbarium',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2E7D32)),
        useMaterial3: true,
      ),
      home: const SeasonCatalogPage(),
    );
  }
}

enum PlantSeason {
  spring('Spring', 'spring', [Color(0xFFA5D6A7), Color(0xFF66BB6A)], Icons.local_florist),
  summer('Summer', 'summer', [Color(0xFFFFCC80), Color(0xFFFF8A65)], Icons.wb_sunny),
  monsoon('Monsoon', 'monsoon', [Color(0xFF80DEEA), Color(0xFF4DB6AC)], Icons.grain),
  autumn('Autumn', 'autumn', [Color(0xFFFFE082), Color(0xFFFFB74D)], Icons.park),
  winter('Winter', 'winter', [Color(0xFFB3E5FC), Color(0xFF90CAF9)], Icons.ac_unit),
  yearRound('Year Round', 'year_round', [Color(0xFFC8E6C9), Color(0xFF81C784)], Icons.eco);

  const PlantSeason(this.label, this.apiCode, this.gradientColors, this.icon);

  final String label;
  final String apiCode;
  final List<Color> gradientColors;
  final IconData icon;
}

class CropInfo {
  const CropInfo({required this.name, required this.subtitle, required this.icon});

  final String name;
  final String subtitle;
  final IconData icon;
}

const Map<PlantSeason, List<CropInfo>> _fallbackSeasonCrops = {
  PlantSeason.spring: [
    CropInfo(name: 'Coriander', subtitle: 'Quick leafy harvest', icon: Icons.spa),
    CropInfo(name: 'Spinach', subtitle: 'Cool-weather greens', icon: Icons.energy_savings_leaf),
    CropInfo(name: 'Mint', subtitle: 'Aromatic and fast spreading', icon: Icons.local_florist),
  ],
  PlantSeason.summer: [
    CropInfo(name: 'Basil', subtitle: 'Heat-friendly herb', icon: Icons.eco),
    CropInfo(name: 'Chili', subtitle: 'Strong sunlight crop', icon: Icons.local_fire_department),
    CropInfo(name: 'Okra', subtitle: 'Performs well in heat', icon: Icons.grass),
  ],
  PlantSeason.monsoon: [
    CropInfo(name: 'Turmeric', subtitle: 'Monsoon planting window', icon: Icons.bubble_chart),
    CropInfo(name: 'Ginger', subtitle: 'Moisture-loving rhizome', icon: Icons.water_drop),
    CropInfo(name: 'Amaranth', subtitle: 'Reliable rainy-season green', icon: Icons.forest),
  ],
  PlantSeason.autumn: [
    CropInfo(name: 'Fenugreek', subtitle: 'Short cycle herb', icon: Icons.eco),
    CropInfo(name: 'Mustard Greens', subtitle: 'Cool transition crop', icon: Icons.energy_savings_leaf),
    CropInfo(name: 'Radish', subtitle: 'Fast maturing root', icon: Icons.spa),
  ],
  PlantSeason.winter: [
    CropInfo(name: 'Carrot', subtitle: 'Best sweetness in cool weather', icon: Icons.grass),
    CropInfo(name: 'Peas', subtitle: 'Winter-friendly climber', icon: Icons.park),
    CropInfo(name: 'Dill', subtitle: 'Cold tolerant herb', icon: Icons.local_florist),
  ],
  PlantSeason.yearRound: [
    CropInfo(name: 'Aloe Vera', subtitle: 'Low-maintenance medicinal plant', icon: Icons.spa),
    CropInfo(name: 'Lemongrass', subtitle: 'Perennial aromatic grass', icon: Icons.grass),
    CropInfo(name: 'Curry Leaf', subtitle: 'Evergreen kitchen tree', icon: Icons.forest),
  ],
};

class SeasonCatalogPage extends StatefulWidget {
  const SeasonCatalogPage({super.key});

  @override
  State<SeasonCatalogPage> createState() => _SeasonCatalogPageState();
}

class _SeasonCatalogPageState extends State<SeasonCatalogPage>
    with SingleTickerProviderStateMixin {
  PlantSeason selectedSeason = PlantSeason.spring;
  late final AnimationController _animationController;
  late final PlantApiService _apiService;
  late Future<List<CropInfo>> _seasonCropsFuture;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat(reverse: true);
    _apiService = PlantApiService();
    _seasonCropsFuture = _loadSeasonCrops(selectedSeason);
  }

  Future<List<CropInfo>> _loadSeasonCrops(PlantSeason season) async {
    try {
      final plants = await _apiService.fetchPlantsBySeason(
        seasonCode: season.apiCode,
        month: DateTime.now().month,
      );
      if (plants.isEmpty) {
        return _fallbackSeasonCrops[season] ?? const [];
      }
      return plants.map(_toCrop).toList();
    } catch (_) {
      return _fallbackSeasonCrops[season] ?? const [];
    }
  }

  CropInfo _toCrop(PlantListItem item) {
    return CropInfo(
      name: item.primaryCommonName.isNotEmpty ? item.primaryCommonName : item.scientificName,
      subtitle:
          '${item.plantType.toUpperCase()} • ${item.lifecycle} • Suitability ${item.suitabilityScore.toStringAsFixed(0)}%',
      icon: _iconForType(item.plantType),
    );
  }

  IconData _iconForType(String plantType) {
    switch (plantType) {
      case 'crop':
        return Icons.grass;
      case 'tree':
        return Icons.forest;
      case 'weed':
        return Icons.warning_amber_rounded;
      case 'herb':
        return Icons.local_florist;
      default:
        return Icons.eco;
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Terra Herbarium'),
        centerTitle: true,
        backgroundColor: Colors.transparent,
      ),
      extendBodyBehindAppBar: true,
      body: Stack(
        children: [
          AnimatedSeasonBackground(
            animation: _animationController,
            colors: selectedSeason.gradientColors,
            icon: selectedSeason.icon,
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 8),
                  const Text(
                    'Select Season',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    height: 44,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: PlantSeason.values
                          .map(
                            (season) => Padding(
                              padding: const EdgeInsets.only(right: 8),
                              child: ChoiceChip(
                                label: Text(season.label),
                                selected: season == selectedSeason,
                                selectedColor: Colors.white,
                                backgroundColor: Colors.white.withValues(alpha: 0.25),
                                side: BorderSide.none,
                                onSelected: (_) {
                                  setState(() {
                                    selectedSeason = season;
                                    _seasonCropsFuture = _loadSeasonCrops(season);
                                  });
                                },
                              ),
                            ),
                          )
                          .toList(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: FutureBuilder<List<CropInfo>>(
                      future: _seasonCropsFuture,
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Center(
                            child: CircularProgressIndicator(color: Colors.white),
                          );
                        }

                        final crops = snapshot.data ?? (_fallbackSeasonCrops[selectedSeason] ?? const []);
                        if (crops.isEmpty) {
                          return const Center(
                            child: Text(
                              'No plants available for this season yet.',
                              style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                            ),
                          );
                        }

                        return ListView.separated(
                          itemCount: crops.length,
                          separatorBuilder: (_, _) => const SizedBox(height: 12),
                          itemBuilder: (context, index) {
                            final crop = crops[index];
                            return CropCard(
                              season: selectedSeason,
                              crop: crop,
                            );
                          },
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class AnimatedSeasonBackground extends StatelessWidget {
  const AnimatedSeasonBackground({
    super.key,
    required this.animation,
    required this.colors,
    required this.icon,
  });

  final Animation<double> animation;
  final List<Color> colors;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: animation,
      builder: (context, child) {
        final shift = math.sin(animation.value * math.pi * 2) * 90;
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment(-1 + shift / 180, -1),
              end: Alignment(1, 1 - shift / 180),
              colors: colors,
            ),
          ),
          child: Stack(
            children: [
              Positioned(
                right: -60,
                top: 110 + shift,
                child: Icon(icon, size: 220, color: Colors.white.withValues(alpha: 0.16)),
              ),
              Positioned(
                left: -30,
                bottom: 70 - shift,
                child: Icon(Icons.grass, size: 180, color: Colors.white.withValues(alpha: 0.12)),
              ),
            ],
          ),
        );
      },
    );
  }
}

class CropCard extends StatelessWidget {
  const CropCard({super.key, required this.season, required this.crop});

  final PlantSeason season;
  final CropInfo crop;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 26,
            backgroundColor: season.gradientColors.last.withValues(alpha: 0.2),
            child: Icon(crop.icon, color: season.gradientColors.last),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  crop.name,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 4),
                Text(
                  crop.subtitle,
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.arrow_forward_ios_rounded, size: 18),
        ],
      ),
    );
  }
}
