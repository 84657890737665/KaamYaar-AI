import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class CameraInputButton extends StatelessWidget {
  const CameraInputButton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFFF6B35).withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ElevatedButton.icon(
        onPressed: () {},
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        icon: const Icon(Icons.camera_alt, color: Color(0xFFFF6B35)),
        label: Text(
          'Camera Input',
          style: GoogleFonts.poppins(color: const Color(0xFFFF6B35), fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}