import 'package:flutter_test/flutter_test.dart';

import 'package:terraherbarium/main.dart';

void main() {
  testWidgets('Season catalog renders', (WidgetTester tester) async {
    await tester.pumpWidget(const TerraHerbariumApp());

    expect(find.text('Terra Herbarium'), findsOneWidget);
    expect(find.text('Select Season'), findsOneWidget);
    expect(find.text('Spring'), findsWidgets);
  });
}
