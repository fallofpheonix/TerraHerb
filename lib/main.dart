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
      title: 'TerraHerb',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2D7A3E)),
        scaffoldBackgroundColor: const Color(0xFFF1F5EB),
      ),
      home: const MarketplacePage(),
    );
  }
}

enum PlantSeason {
  spring('Spring', 'spring'),
  summer('Summer', 'summer'),
  monsoon('Monsoon', 'monsoon'),
  autumn('Autumn', 'autumn'),
  winter('Winter', 'winter'),
  yearRound('Year Round', 'year_round');

  const PlantSeason(this.label, this.apiCode);

  final String label;
  final String apiCode;
}

class CropInfo {
  const CropInfo({required this.name, required this.subtitle, required this.icon, required this.price});

  final String name;
  final String subtitle;
  final IconData icon;
  final int price;
}

const Map<PlantSeason, List<CropInfo>> _fallbackSeasonCrops = {
  PlantSeason.spring: [
    CropInfo(name: 'Bok Choy', subtitle: '3 weeks • 12 seed/pack', icon: Icons.eco, price: 14),
    CropInfo(name: 'Lettuce', subtitle: '3 weeks • 12 seed/pack', icon: Icons.grass, price: 14),
    CropInfo(name: 'Convolvulus', subtitle: '3 months • 12 seed/pack', icon: Icons.spa, price: 12),
  ],
  PlantSeason.summer: [
    CropInfo(name: 'Amaranth', subtitle: '2 weeks • 18 seed/pack', icon: Icons.energy_savings_leaf, price: 10),
    CropInfo(name: 'Okra', subtitle: '6 weeks • 10 seed/pack', icon: Icons.local_florist, price: 15),
    CropInfo(name: 'Chili', subtitle: '8 weeks • 20 seed/pack', icon: Icons.local_fire_department, price: 11),
  ],
  PlantSeason.monsoon: [
    CropInfo(name: 'Turmeric', subtitle: '10 weeks • 8 rhizomes', icon: Icons.spa, price: 16),
    CropInfo(name: 'Ginger', subtitle: '8 weeks • 10 rhizomes', icon: Icons.water_drop, price: 13),
    CropInfo(name: 'Mint', subtitle: '4 weeks • starter set', icon: Icons.eco, price: 9),
  ],
  PlantSeason.autumn: [
    CropInfo(name: 'Fenugreek', subtitle: '2 weeks • 20 seed/pack', icon: Icons.grass, price: 9),
    CropInfo(name: 'Mustard', subtitle: '3 weeks • 18 seed/pack', icon: Icons.energy_savings_leaf, price: 10),
    CropInfo(name: 'Radish', subtitle: '5 weeks • 16 seed/pack', icon: Icons.spa, price: 11),
  ],
  PlantSeason.winter: [
    CropInfo(name: 'Carrot', subtitle: '7 weeks • 20 seed/pack', icon: Icons.grass, price: 13),
    CropInfo(name: 'Peas', subtitle: '6 weeks • 15 seed/pack', icon: Icons.park, price: 12),
    CropInfo(name: 'Dill', subtitle: '4 weeks • 18 seed/pack', icon: Icons.eco, price: 8),
  ],
  PlantSeason.yearRound: [
    CropInfo(name: 'Tulsi', subtitle: '4 weeks • starter set', icon: Icons.local_florist, price: 10),
    CropInfo(name: 'Lemongrass', subtitle: '6 weeks • starter set', icon: Icons.grass, price: 11),
    CropInfo(name: 'Curry Leaf', subtitle: '8 weeks • sapling', icon: Icons.forest, price: 17),
  ],
};

class MarketplacePage extends StatefulWidget {
  const MarketplacePage({super.key});

  @override
  State<MarketplacePage> createState() => _MarketplacePageState();
}

class _MarketplacePageState extends State<MarketplacePage> {
  PlantSeason _selectedSeason = PlantSeason.spring;
  late final PlantApiService _apiService;
  late Future<List<CropInfo>> _cropsFuture;

  @override
  void initState() {
    super.initState();
    _apiService = PlantApiService();
    _cropsFuture = _loadSeasonCrops(_selectedSeason);
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
      subtitle: '${item.lifecycle} • suitability ${item.suitabilityScore.toStringAsFixed(0)}%',
      icon: _iconForType(item.plantType),
      price: 14,
    );
  }

  IconData _iconForType(String type) {
    switch (type) {
      case 'herb':
        return Icons.local_florist;
      case 'tree':
        return Icons.forest;
      case 'crop':
        return Icons.grass;
      default:
        return Icons.eco;
    }
  }

  void _selectSeason(PlantSeason season) {
    setState(() {
      _selectedSeason = season;
      _cropsFuture = _loadSeasonCrops(season);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final wide = constraints.maxWidth >= 1080;
            return Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                children: [
                  _SeasonChips(selected: _selectedSeason, onSelected: _selectSeason),
                  const SizedBox(height: 14),
                  Expanded(
                    child: FutureBuilder<List<CropInfo>>(
                      future: _cropsFuture,
                      builder: (context, snapshot) {
                        final crops = snapshot.data ?? (_fallbackSeasonCrops[_selectedSeason] ?? const []);
                        if (wide) {
                          return _DesktopLayout(crops: crops);
                        }
                        return _MobileLayout(crops: crops);
                      },
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _SeasonChips extends StatelessWidget {
  const _SeasonChips({required this.selected, required this.onSelected});

  final PlantSeason selected;
  final ValueChanged<PlantSeason> onSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemBuilder: (context, index) {
          final season = PlantSeason.values[index];
          return ChoiceChip(
            label: Text(season.label),
            selected: selected == season,
            onSelected: (_) => onSelected(season),
            selectedColor: const Color(0xFF8BE044),
            labelStyle: TextStyle(
              color: selected == season ? const Color(0xFF103619) : const Color(0xFF2F4732),
              fontWeight: FontWeight.w600,
            ),
            side: BorderSide.none,
            backgroundColor: Colors.white,
          );
        },
        separatorBuilder: (_, _) => const SizedBox(width: 8),
        itemCount: PlantSeason.values.length,
      ),
    );
  }
}

class _DesktopLayout extends StatelessWidget {
  const _DesktopLayout({required this.crops});

  final List<CropInfo> crops;

  @override
  Widget build(BuildContext context) {
    final first = crops.isNotEmpty ? crops.first : const CropInfo(name: 'Bok Choy', subtitle: '3 weeks • 12 seed/pack', icon: Icons.eco, price: 14);
    final second = crops.length > 1 ? crops[1] : first;

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFDDE8D4),
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        children: [
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: _ExplorePanel(primary: first),
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: _SeasonPanel(crops: crops),
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: _DetailPanel(primary: first, secondary: second),
            ),
          ),
        ],
      ),
    );
  }
}

class _MobileLayout extends StatelessWidget {
  const _MobileLayout({required this.crops});

  final List<CropInfo> crops;

  @override
  Widget build(BuildContext context) {
    final first = crops.isNotEmpty ? crops.first : const CropInfo(name: 'Bok Choy', subtitle: '3 weeks • 12 seed/pack', icon: Icons.eco, price: 14);
    final second = crops.length > 1 ? crops[1] : first;

    return ListView(
      children: [
        SizedBox(height: 420, child: _ExplorePanel(primary: first)),
        const SizedBox(height: 12),
        SizedBox(height: 500, child: _SeasonPanel(crops: crops)),
        const SizedBox(height: 12),
        SizedBox(height: 620, child: _DetailPanel(primary: first, secondary: second)),
      ],
    );
  }
}

class _ExplorePanel extends StatelessWidget {
  const _ExplorePanel({required this.primary});

  final CropInfo primary;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0D4A24), Color(0xFF1F7035)],
        ),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  'Explore\na wide\nvariety of\nseeds',
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 24, height: 1.1),
                ),
              ),
              _LeafBadge(icon: primary.icon),
            ],
          ),
          const Spacer(),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
            decoration: BoxDecoration(color: const Color(0xFF8BE044), borderRadius: BorderRadius.circular(16)),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.eco, color: Color(0xFF0D3A18)),
                SizedBox(width: 8),
                Text('Start your green journey!', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF0D3A18))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SeasonPanel extends StatelessWidget {
  const _SeasonPanel({required this.crops});

  final List<CropInfo> crops;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(colors: [Color(0xFF0F5A2B), Color(0xFF0A3D1E)], begin: Alignment.topLeft, end: Alignment.bottomRight),
      ),
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.wb_sunny, color: Colors.amber, size: 34),
              const SizedBox(width: 8),
              const Expanded(
                child: Text('Sunny, 30°\nMonday, 13 Feb 2024', style: TextStyle(color: Colors.white70, fontSize: 18, height: 1.2)),
              ),
              CircleAvatar(
                radius: 20,
                backgroundColor: Colors.white24,
                child: IconButton(
                  padding: EdgeInsets.zero,
                  icon: const Icon(Icons.shopping_cart, color: Colors.white),
                  onPressed: () {},
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text('Perfect for\nthis season!', style: TextStyle(color: Colors.white, fontSize: 50, fontWeight: FontWeight.w600, height: 0.95)),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.separated(
              itemBuilder: (context, index) => _SeedCard(crop: crops[index]),
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemCount: crops.length,
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 18),
            decoration: BoxDecoration(color: const Color(0xFFDDE8D4), borderRadius: BorderRadius.circular(24)),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.home, color: Color(0xFF123A1D)),
                SizedBox(width: 18),
                Icon(Icons.article, color: Color(0xFF56785D)),
                SizedBox(width: 18),
                Icon(Icons.person, color: Color(0xFF56785D)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailPanel extends StatelessWidget {
  const _DetailPanel({required this.primary, required this.secondary});

  final CropInfo primary;
  final CropInfo secondary;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Container(
          decoration: BoxDecoration(color: const Color(0xFF0E4D27), borderRadius: BorderRadius.circular(24)),
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Align(
                alignment: Alignment.centerLeft,
                child: CircleAvatar(
                  backgroundColor: const Color(0xFFDDE8D4),
                  child: IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.arrow_back, color: Color(0xFF1A4825)),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Text(primary.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 40)),
              const SizedBox(height: 6),
              Text(primary.subtitle, style: const TextStyle(color: Colors.white70, fontSize: 20)),
              const SizedBox(height: 20),
              const Text('Choose the Right Location\n• 6+ hours direct sunlight\n• Well-drained rich soil', style: TextStyle(color: Colors.white70, height: 1.4, fontSize: 17)),
              const SizedBox(height: 16),
              const Text('Prepare the Soil\n• Loosen top 8 inches\n• Mix compost and organic matter', style: TextStyle(color: Colors.white70, height: 1.4, fontSize: 17)),
              const Spacer(),
              Align(
                alignment: Alignment.bottomRight,
                child: Container(
                  decoration: BoxDecoration(color: const Color(0xFF8BE044), borderRadius: BorderRadius.circular(20)),
                  child: IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.shopping_cart, size: 30, color: Color(0xFF123A1D)),
                  ),
                ),
              ),
            ],
          ),
        ),
        Positioned(
          right: 4,
          top: 140,
          child: _FloatingSeedCard(crop: secondary),
        ),
      ],
    );
  }
}

class _SeedCard extends StatelessWidget {
  const _SeedCard({required this.crop});

  final CropInfo crop;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(22)),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: const Color(0xFFDDE8D4), borderRadius: BorderRadius.circular(10)),
                  child: Text('\$${crop.price}', style: const TextStyle(fontWeight: FontWeight.w700, color: Color(0xFF184625))),
                ),
                const SizedBox(height: 8),
                Text(crop.name, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 28, color: Color(0xFF184625))),
                const SizedBox(height: 4),
                Text(crop.subtitle, style: const TextStyle(color: Color(0xFF5F7E66), fontSize: 18)),
                const SizedBox(height: 8),
                Container(
                  decoration: BoxDecoration(color: const Color(0xFF8BE044), borderRadius: BorderRadius.circular(14)),
                  child: IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.shopping_cart, color: Color(0xFF123A1D)),
                  ),
                ),
              ],
            ),
          ),
          _LeafBadge(icon: crop.icon),
        ],
      ),
    );
  }
}

class _FloatingSeedCard extends StatelessWidget {
  const _FloatingSeedCard({required this.crop});

  final CropInfo crop;

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: -0.12,
      child: SizedBox(
        width: 320,
        child: _SeedCard(crop: crop),
      ),
    );
  }
}

class _LeafBadge extends StatelessWidget {
  const _LeafBadge({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 110,
      height: 110,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: const Color(0xFFDDE8D4),
        border: Border.all(color: Colors.white54, width: 3),
      ),
      child: Icon(icon, size: 56, color: const Color(0xFF2D7A3E)),
    );
  }
}
