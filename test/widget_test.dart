import 'package:flutter_test/flutter_test.dart';

import 'package:terraherbarium/main.dart';

void main() {
  testWidgets('Marketplace UI renders core sections', (WidgetTester tester) async {
    await tester.pumpWidget(const TerraHerbariumApp());

    expect(find.text('Explore\na wide\nvariety of\nseeds'), findsOneWidget);
    expect(find.text('Perfect for\nthis season!'), findsOneWidget);
    expect(find.text('Start your green journey!'), findsOneWidget);
    expect(find.text('Spring'), findsWidgets);
  });
}
