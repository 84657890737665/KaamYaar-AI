import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../widgets/verified_badge.dart';
import 'safety_timer_screen.dart';
import 'trusted_contact_screen.dart';

class CnicFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(TextEditingValue oldValue, TextEditingValue newValue) {
    final String text = newValue.text;
    if (newValue.selection.baseOffset == 0) {
      return newValue;
    }
    final StringBuffer buffer = StringBuffer();
    int selectionIndex = newValue.selection.end;
    final String digits = text.replaceAll(RegExp(r'\D'), '');
    for (int i = 0; i < digits.length; i++) {
      if (i == 5) {
        buffer.write('-');
      } else if (i == 12) {
        buffer.write('-');
      }
      buffer.write(digits[i]);
    }
    final String formattedText = buffer.toString();
    int delta = formattedText.length - text.length;
    selectionIndex += delta;
    return TextEditingValue(
      text: formattedText,
      selection: TextSelection.collapsed(offset: selectionIndex.clamp(0, formattedText.length)),
    );
  }
}

class MobileFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(TextEditingValue oldValue, TextEditingValue newValue) {
    final String text = newValue.text;
    if (newValue.selection.baseOffset == 0) {
      return newValue;
    }
    final StringBuffer buffer = StringBuffer();
    int selectionIndex = newValue.selection.end;
    final String digits = text.replaceAll(RegExp(r'\D'), '');
    for (int i = 0; i < digits.length; i++) {
      if (i == 4) {
        buffer.write('-');
      }
      buffer.write(digits[i]);
    }
    final String formattedText = buffer.toString();
    int delta = formattedText.length - text.length;
    selectionIndex += delta;
    return TextEditingValue(
      text: formattedText,
      selection: TextSelection.collapsed(offset: selectionIndex.clamp(0, formattedText.length)),
    );
  }
}

class FemaleSafetyBookingScreen extends StatefulWidget {
  final Map<String, dynamic> provider;
  const FemaleSafetyBookingScreen({super.key, required this.provider});

  @override
  State<FemaleSafetyBookingScreen> createState() => _FemaleSafetyBookingScreenState();
}

class _FemaleSafetyBookingScreenState extends State<FemaleSafetyBookingScreen> {
  final TextEditingController _cnicController = TextEditingController();
  final TextEditingController _mobileController = TextEditingController();

  Map<String, dynamic> get provider => widget.provider;

  @override
  void dispose() {
    _cnicController.dispose();
    _mobileController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final String serviceTypes = (provider['service_types'] as List).join(', ');

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FD),
      appBar: AppBar(
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF880E4F), Color(0xFFAD1457)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Safe Booking',
          style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.security, color: Colors.white),
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSafetyBanner(),
            const SizedBox(height: 20),
            _buildProviderInfo(serviceTypes),
            const SizedBox(height: 20),
            _buildBookingDetails(),
            const SizedBox(height: 20),
            _buildPriceBreakdown(),
            const SizedBox(height: 20),
            _buildShareSection(context),
            const SizedBox(height: 100),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                offset: const Offset(0, -4),
                blurRadius: 10,
              ),
            ],
          ),
          child: Container(
            width: double.infinity,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF2E7D32), Color(0xFF43A047)],
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF2E7D32).withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: () {
                // Navigate to actual SafetyTimerScreen
                Navigator.push(context, MaterialPageRoute(builder: (context) => SafetyTimerScreen(provider: provider)));
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              ),
              child: Text('✓ Confirm Booking', style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSafetyBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFD81B60), Color(0xFFF06292)],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFD81B60).withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          const Icon(Icons.shield, color: Colors.white, size: 48),
          const SizedBox(height: 12),
          Text(
            'Your Safety is Our Priority',
            style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          Text(
            'Provider is CNIC Verified ✓',
            style: GoogleFonts.poppins(color: Colors.white, fontSize: 13),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildProviderInfo(String serviceTypes) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: const Color(0xFFD81B60), width: 3),
              color: Colors.grey[200],
            ),
            child: const Center(child: Icon(Icons.person, size: 40, color: Colors.grey)),
          ),
          const SizedBox(height: 16),
          Text(
            provider['name'],
            style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const VerifiedBadge(),
          const SizedBox(height: 16),
          _buildReadOnlyField(
            icon: Icons.lock,
            label: 'CNIC Number',
            value: '35201-XXXXXX-X',
          ),
          const SizedBox(height: 12),
          _buildReadOnlyField(
            icon: Icons.phone,
            label: 'Mobile',
            value: '0300-XXXXXXX',
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(_capitalize(serviceTypes), style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14)),
              const SizedBox(width: 12),
              const Icon(Icons.star, color: Colors.amber, size: 16),
              Text(' ${provider['rating']}', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 14)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildReadOnlyField({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFFD81B60), size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: GoogleFonts.poppins(fontSize: 11, color: Colors.grey[600], fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: GoogleFonts.poppins(fontSize: 14, color: Colors.grey[800], fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBookingDetails() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Booking Details', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 18, color: const Color(0xFF0A2463))),
          const SizedBox(height: 16),
          _detailRow(Icons.build, 'Service', _capitalize((provider['service_types'] as List).join(', '))),
          _detailRow(Icons.calendar_today, 'Date', 'Today'),
          _detailRow(Icons.access_time, 'Time', '3:00 PM'),
          _detailRow(Icons.location_on, 'Location', provider['location_name']),
          const Divider(height: 32),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF3E0),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFFFCC80)),
            ),
            child: Row(
              children: [
                const Icon(Icons.schedule, color: Color(0xFFE65100), size: 32),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('AI Estimated Arrival', style: GoogleFonts.poppins(color: const Color(0xFFE65100), fontSize: 12)),
                      Text('~45 minutes', style: GoogleFonts.poppins(color: const Color(0xFFE65100), fontWeight: FontWeight.bold, fontSize: 20)),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: Colors.green[50], borderRadius: BorderRadius.circular(8)),
                  child: Text('AI Confidence: 94%', style: GoogleFonts.poppins(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 10)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _detailRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: const Color(0xFF1565C0), size: 18),
          const SizedBox(width: 12),
          Text(label, style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14)),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              value,
              style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: Colors.black87, fontSize: 14),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShareSection(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Share with Trusted Contact 👥', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 16, color: const Color(0xFF0A2463))),
          const SizedBox(height: 16),
          TextField(
            style: GoogleFonts.poppins(),
            decoration: InputDecoration(
              hintText: 'Enter contact name or number',
              hintStyle: GoogleFonts.poppins(color: Colors.grey[400]),
              filled: true,
              fillColor: Colors.grey[50],
              prefixIcon: const Icon(Icons.contacts, color: Color(0xFFD81B60)),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.grey[200]!)),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFFD81B60))),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFFD81B60), Color(0xFFF06292)]),
              borderRadius: BorderRadius.circular(12),
            ),
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => TrustedContactScreen(provider: provider),
                  ),
                );
              },
              icon: const Icon(Icons.ios_share, color: Colors.white, size: 18),
              label: Text('Share Booking Details', style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold)),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPriceBreakdown() {
    final int baseRate = provider['base_rate_pkr'] ?? 0;
    final int distanceFee = ((provider['distance_km'] ?? 0.0) * 50).round();
    final int serviceTax = (baseRate * 0.05).round();
    final int total = baseRate + distanceFee + serviceTax;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Price Breakdown',
            style: GoogleFonts.poppins(
              fontWeight: FontWeight.bold,
              fontSize: 18,
              color: const Color(0xFF0A2463),
            ),
          ),
          const SizedBox(height: 16),
          _priceRow('Base Rate', baseRate),
          const SizedBox(height: 12),
          _priceRow('Distance Fee', distanceFee),
          const SizedBox(height: 12),
          _priceRow('Service Tax (5%)', serviceTax),
          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Total',
                style: GoogleFonts.poppins(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF0A2463),
                ),
              ),
              Text(
                'Rs. $total',
                style: GoogleFonts.poppins(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF2E7D32),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _priceRow(String title, int amount) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: GoogleFonts.poppins(color: Colors.grey[700], fontSize: 14),
        ),
        Text(
          'Rs. $amount',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.bold,
            color: Colors.black87,
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  String _capitalize(String text) {
    if (text.isEmpty) return text;
    return text.replaceAll('_', ' ').split(' ').map((word) {
      if (word.isEmpty) return word;
      return word[0].toUpperCase() + word.substring(1);
    }).join(' ');
  }
}
