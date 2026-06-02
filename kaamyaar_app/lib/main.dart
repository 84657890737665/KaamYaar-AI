import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const KaamYaarApp());
}

class KaamYaarApp extends StatelessWidget {
  const KaamYaarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KaamYaar AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1565C0),
        ),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}