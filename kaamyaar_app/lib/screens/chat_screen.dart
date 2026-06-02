import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class ChatScreen extends StatelessWidget {
  final Map<String, dynamic> provider;
  const ChatScreen({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Chat', style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold)),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(colors: [Color(0xFF0D47A1), Color(0xFF1976D2)]),
          ),
        ),
      ),
      body: Center(
        child: Text('Chat feature coming soon!',
            style: GoogleFonts.poppins(fontSize: 16, color: Colors.grey)),
      ),
    );
  }
}