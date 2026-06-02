import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class ProviderHomeScreen extends StatelessWidget {
  final String name;
  final String cnic;
  final String mobile;
  final String services;
  final String experience;
  final bool isVerified;

  const ProviderHomeScreen({
    super.key,
    this.name = 'Ahmed Khan',
    this.cnic = '35201-1234567-1',
    this.mobile = '0300-1234567',
    this.services = 'AC Repair, Plumbing, Electrical',
    this.experience = '5',
    this.isVerified = false,
  });

  String _maskCnic(String val) {
    if (val.length >= 12) {
      final parts = val.split('-');
      if (parts.length == 3) {
        return '${parts[0]}-XXXXXXX-${parts[2]}';
      }
    }
    if (val.length > 6) {
      return '${val.substring(0, 5)}...${val.substring(val.length - 2)}';
    }
    return val;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4FF),
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(kToolbarHeight),
        child: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF0A2463), Color(0xFF1565C0)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: AppBar(
            backgroundColor: Colors.transparent,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => Navigator.pop(context),
            ),
            title: Text(
              'Provider Dashboard',
              style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold),
            ),
            centerTitle: true,
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 600),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Welcome card
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF1565C0), Color(0xFF42A5F5)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF1565C0).withOpacity(0.3),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome Back, $name! 👋',
                        style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        isVerified
                            ? 'Aapka account verified hai! ✓'
                            : 'Aapka account verified ho raha hai ⏳',
                        style: GoogleFonts.poppins(color: Colors.white.withOpacity(0.9), fontSize: 15, fontWeight: FontWeight.w500),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Registration details profile card
                Text(
                  'Registration Profile',
                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
                ),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
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
                      _buildProfileRow('Full Name', name, Icons.person_outline),
                      const Divider(height: 20),
                      _buildProfileRow('CNIC Number', _maskCnic(cnic), Icons.badge_outlined),
                      const Divider(height: 20),
                      _buildProfileRow('Mobile Number', mobile, Icons.phone_android),
                      const Divider(height: 20),
                      _buildProfileRow('Experience', '$experience Years', Icons.work_outline),
                      const Divider(height: 20),
                      _buildProfileRow('Services Offered', services, Icons.handyman_outlined),
                    ],
                  ),
                ),
                const SizedBox(height: 28),

                // Stats cards row
                Row(
                  children: [
                    Expanded(
                      child: _buildStatCard(
                        value: '0',
                        label: 'Bookings',
                        color: const Color(0xFF1565C0),
                        icon: Icons.assignment_outlined,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildStatCard(
                        value: '0',
                        label: 'Reviews',
                        color: const Color(0xFFFF6B35),
                        icon: Icons.star_outline,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildStatCard(
                        value: isVerified ? 'Verified' : 'Pending',
                        label: 'Verification',
                        color: isVerified ? const Color(0xFF2E7D32) : const Color(0xFFE65100),
                        icon: isVerified ? Icons.verified_user : Icons.hourglass_empty,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),

                // My Services section
                Text(
                  'Offered Services Preview',
                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
                ),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
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
                    children: services.split(',').map((serv) {
                      final trimServ = serv.trim();
                      if (trimServ.isEmpty) return const SizedBox.shrink();
                      return Column(
                        children: [
                          _buildServiceItem(trimServ, Icons.check_circle_outline, Colors.blue),
                          const Divider(height: 16),
                        ],
                      );
                    }).toList()
                      ..add(const Column(children: [])), // placeholder
                  ),
                ),
                const SizedBox(height: 32),

                // Action buttons
                _buildActionButton(
                  text: 'View Booking Requests',
                  gradient: const LinearGradient(colors: [Color(0xFF0D47A1), Color(0xFF1976D2)]),
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('No new booking requests at the moment.', style: GoogleFonts.poppins()),
                        backgroundColor: const Color(0xFF0A2463),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 16),
                _buildActionButton(
                  text: 'Update Profile',
                  gradient: const LinearGradient(colors: [Color(0xFFFF6B35), Color(0xFFFF8C42)]),
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Profile update section is locked during verification.', style: GoogleFonts.poppins()),
                        backgroundColor: const Color(0xFFFF6B35),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildProfileRow(String label, String value, IconData icon) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: const Color(0xFF1565C0), size: 20),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: GoogleFonts.poppins(fontSize: 11, color: Colors.grey[500], fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.black87),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String value,
    required String label,
    required Color color,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
        border: Border.all(color: color.withOpacity(0.1), width: 1.5),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 10),
          Text(
            value,
            style: GoogleFonts.poppins(
              fontSize: value.length > 5 ? 14 : 18,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF0A2463),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: GoogleFonts.poppins(fontSize: 12, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildServiceItem(String title, IconData icon, MaterialColor color) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color[50],
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color[700], size: 20),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Text(
            title,
            style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.black87),
          ),
        ),
        const Icon(Icons.check_circle, color: Colors.green, size: 18),
      ],
    );
  }

  Widget _buildActionButton({
    required String text,
    required Gradient gradient,
    required VoidCallback onPressed,
  }) {
    return Container(
      width: double.infinity,
      height: 54,
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
        child: Text(
          text,
          style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
        ),
      ),
    );
  }
}
