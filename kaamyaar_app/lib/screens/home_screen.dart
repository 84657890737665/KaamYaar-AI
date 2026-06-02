import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'request_input_screen.dart';
import 'provider_results_screen.dart';
import 'login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ScrollController _scrollController = ScrollController();
  final GlobalKey _servicesKey = GlobalKey();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: const Color(0xFF0A2463),
        elevation: 0,
        toolbarHeight: 50,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const LoginScreen()),
          ),
        ),
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isMobile = constraints.maxWidth < 800;
          return SingleChildScrollView(
            controller: _scrollController,
            child: Column(
              children: [
                _buildNavBar(context, isMobile),
                _buildHeroSection(context, isMobile),
                _buildServicesSection(isMobile),
                _buildHowItWorksSection(isMobile),
                _buildNearbyProvidersSection(isMobile),
                _buildFooter(isMobile),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildNavBar(BuildContext context, bool isMobile) {
    return Container(
      height: 70,
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: EdgeInsets.symmetric(horizontal: isMobile ? 20 : 60),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Logo
          Row(
            children: [
              Text(
                'KaamYaar AI ',
                style: GoogleFonts.poppins(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1565C0),
                ),
              ),
              const Text('⚡', style: TextStyle(fontSize: 22)),
            ],
          ),
          
          if (!isMobile)
            Row(
              children: [
                _navLink('Home', () {
                  _scrollController.animateTo(0, duration: const Duration(milliseconds: 500), curve: Curves.easeInOut);
                }),
                const SizedBox(width: 24),
                _navLink('Services', () {
                  if (_servicesKey.currentContext != null) {
                    Scrollable.ensureVisible(
                      _servicesKey.currentContext!,
                      duration: const Duration(milliseconds: 500),
                      curve: Curves.easeInOut,
                    );
                  }
                }),
                const SizedBox(width: 24),
                _navLink('Providers', () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => const ProviderResultsScreen()));
                }),
                const SizedBox(width: 24),
                _navLink('About', () {
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('About KaamYaar AI'),
                      content: const Text('Pakistan ka #1 AI-powered service platform. Connecting skilled workers with customers since 2024.'),
                      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK'))],
                    )
                  );
                }),
              ],
            ),
            
          // Button
          Container(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFFFF6B35), Color(0xFFFF8C42)],
              ),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFFFF6B35).withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (context) => const RequestInputScreen()));
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                padding: EdgeInsets.symmetric(horizontal: isMobile ? 16 : 24, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
              ),
              child: Text(
                'Get Started',
                style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _navLink(String title, VoidCallback onTap) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: onTap,
        child: Text(
          title,
          style: GoogleFonts.poppins(
            color: Colors.black87,
            fontWeight: FontWeight.w600,
            fontSize: 15,
          ),
        ),
      ),
    );
  }

  Widget _buildHeroSection(BuildContext context, bool isMobile) {
    return Container(
      width: double.infinity,
      constraints: const BoxConstraints(minHeight: 500),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [Color(0xFF0A2463), Color(0xFF1565C0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      padding: EdgeInsets.symmetric(horizontal: isMobile ? 20 : 60, vertical: 60),
      child: isMobile
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                _buildHeroContent(context, true),
                const SizedBox(height: 60),
                _buildHeroStats(true),
              ],
            )
          : Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(child: _buildHeroContent(context, false)),
                const SizedBox(width: 40),
                Expanded(child: _buildHeroStats(false)),
              ],
            ),
    );
  }

  Widget _buildHeroContent(BuildContext context, bool isMobile) {
    return Column(
      crossAxisAlignment: isMobile ? CrossAxisAlignment.center : CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFFFF6B35),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            'Pakistan #1 Service App 🇵🇰',
            style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
          ),
        ),
        const SizedBox(height: 24),
        Text(
          'Find Trusted\nService Providers\nNear You',
          textAlign: isMobile ? TextAlign.center : TextAlign.left,
          style: GoogleFonts.poppins(
            color: Colors.white,
            fontSize: isMobile ? 36 : 48,
            fontWeight: FontWeight.bold,
            height: 1.2,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'AI-powered matching for AC, Plumber, Cook & more',
          textAlign: isMobile ? TextAlign.center : TextAlign.left,
          style: GoogleFonts.poppins(
            color: Colors.white60,
            fontSize: isMobile ? 16 : 18,
          ),
        ),
        const SizedBox(height: 40),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: isMobile ? WrapAlignment.center : WrapAlignment.start,
          children: [
            Container(
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFFF6B35), Color(0xFFFF8C42)],
                ),
                borderRadius: BorderRadius.circular(30),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFFFF6B35).withOpacity(0.4),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => const RequestInputScreen()));
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                ),
                child: Text('Request Service →', style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              ),
            ),
            OutlinedButton(
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (context) => const ProviderResultsScreen()));
              },
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.white, width: 2),
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              ),
              child: Text('View Providers', style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildHeroStats(bool isMobile) {
    return Center(
      child: Wrap(
        spacing: 20,
        runSpacing: 20,
        alignment: WrapAlignment.center,
        children: [
          _statCard('500+', 'Providers', Colors.blue, Icons.people),
          _statCard('4.9★', 'Rating', Colors.orange, Icons.star),
          _statCard('24/7', 'Support', Colors.green, Icons.support_agent),
        ],
      ),
    );
  }

  Widget _statCard(String value, String label, MaterialColor color, IconData icon) {
    return Container(
      width: 140,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color[50],
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color[700], size: 32),
          ),
          const SizedBox(height: 16),
          Text(
            value,
            style: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
          ),
          Text(
            label,
            style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildServicesSection(bool isMobile) {
    final services = [
      {'name': 'AC Repair', 'icon': Icons.ac_unit, 'colors': [const Color(0xFFFF6B35), const Color(0xFFFF8C42)]},
      {'name': 'Plumbing', 'icon': Icons.plumbing, 'colors': [const Color(0xFF1565C0), const Color(0xFF1976D2)]},
      {'name': 'Cooking', 'icon': Icons.restaurant, 'colors': [const Color(0xFF2E7D32), const Color(0xFF388E3C)]},
      {'name': 'Beauty', 'icon': Icons.face_retouching_natural, 'colors': [const Color(0xFFAD1457), const Color(0xFFD81B60)]},
      {'name': 'Carpentry', 'icon': Icons.handyman, 'colors': [const Color(0xFF4E342E), const Color(0xFF6D4C41)]},
      {'name': 'Electrical', 'icon': Icons.bolt, 'colors': [const Color(0xFFF9A825), const Color(0xFFFBC02D)]},
      {'name': 'Painting', 'icon': Icons.format_paint, 'colors': [const Color(0xFF6A1B9A), const Color(0xFF7B1FA2)]},
      {'name': 'Mechanic', 'icon': Icons.build, 'colors': [const Color(0xFF00695C), const Color(0xFF00796B)]},
    ];

    return Container(
      key: _servicesKey,
      color: Colors.white,
      padding: EdgeInsets.symmetric(horizontal: isMobile ? 20 : 60, vertical: 80),
      child: Column(
        children: [
          Text(
            'Our Services',
            style: GoogleFonts.poppins(fontSize: 36, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            'Professional services at your doorstep',
            style: GoogleFonts.poppins(fontSize: 16, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 60),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: isMobile ? 2 : 4,
              crossAxisSpacing: 20,
              mainAxisSpacing: 20,
              childAspectRatio: isMobile ? 0.85 : 1.0,
            ),
            itemCount: services.length,
            itemBuilder: (context, index) {
              final service = services[index];
              final colors = service['colors'] as List<Color>;
              return GestureDetector(
                onTap: () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => const RequestInputScreen()));
                },
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.05),
                          blurRadius: 15,
                          offset: const Offset(0, 5),
                        ),
                      ],
                      border: Border.all(color: Colors.grey[100]!),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(colors: colors, begin: Alignment.topLeft, end: Alignment.bottomRight),
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(color: colors[0].withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4)),
                            ],
                          ),
                          child: Icon(service['icon'] as IconData, color: Colors.white, size: 32),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          service['name'] as String,
                          style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.black87),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Book Now',
                          style: GoogleFonts.poppins(color: const Color(0xFFFF6B35), fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildHowItWorksSection(bool isMobile) {
    return Container(
      width: double.infinity,
      color: const Color(0xFFF0F4FF),
      padding: EdgeInsets.symmetric(horizontal: isMobile ? 20 : 60, vertical: 80),
      child: Column(
        children: [
          Text(
            'How It Works',
            style: GoogleFonts.poppins(fontSize: 36, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 60),
          isMobile
              ? Column(
                  children: [
                    _stepCard('1', '📝', 'Request', 'Describe your need'),
                    const SizedBox(height: 24),
                    _stepCard('2', '🤖', 'AI Matches', 'We find best provider'),
                    const SizedBox(height: 24),
                    _stepCard('3', '✅', 'Get Service', 'Provider arrives'),
                  ],
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Expanded(child: _stepCard('1', '📝', 'Request', 'Describe your need')),
                    const SizedBox(width: 40),
                    Expanded(child: _stepCard('2', '🤖', 'AI Matches', 'We find best provider')),
                    const SizedBox(width: 40),
                    Expanded(child: _stepCard('3', '✅', 'Get Service', 'Provider arrives')),
                  ],
                ),
        ],
      ),
    );
  }

  Widget _stepCard(String number, String emoji, String title, String desc) {
    return Column(
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4)),
            ],
          ),
          child: Stack(
            children: [
              Center(child: Text(emoji, style: const TextStyle(fontSize: 32))),
              Positioned(
                top: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.all(6),
                  decoration: const BoxDecoration(color: Color(0xFFFF6B35), shape: BoxShape.circle),
                  child: Text(number, style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        Text(title, style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463))),
        const SizedBox(height: 8),
        Text(desc, style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14)),
      ],
    );
  }

  Widget _buildNearbyProvidersSection(bool isMobile) {
    final providers = [
      {'name': 'Ali AC Services', 'service': 'AC Technician', 'rating': '4.9', 'distance': '1.5 km', 'price': 'Rs.1000', 'initials': 'AA', 'color': const Color(0xFFFF6B35)},
      {'name': 'Bilal Carpenter', 'service': 'Carpenter', 'rating': '4.6', 'distance': '6.9 km', 'price': 'Rs.1000', 'initials': 'BC', 'color': const Color(0xFF4E342E)},
      {'name': 'Fatima Beautician', 'service': 'Beautician', 'rating': '4.2', 'distance': '3.3 km', 'price': 'Rs.1600', 'initials': 'FB', 'color': const Color(0xFFAD1457)},
      {'name': 'Sajid Plumber', 'service': 'Plumbing', 'rating': '4.8', 'distance': '2.1 km', 'price': 'Rs.1200', 'initials': 'SP', 'color': const Color(0xFF1565C0)},
    ];

    return Container(
      color: Colors.white,
      padding: EdgeInsets.symmetric(vertical: 80, horizontal: isMobile ? 20 : 60),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Top Rated Providers',
            style: GoogleFonts.poppins(fontSize: 32, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
          ),
          const SizedBox(height: 40),
          SizedBox(
            height: 220,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: providers.length,
              itemBuilder: (context, index) {
                final p = providers[index];
                return Container(
                  width: 260,
                  margin: const EdgeInsets.only(right: 24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.grey[200]!),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.04),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              width: 50,
                              height: 50,
                              decoration: BoxDecoration(
                                color: (p['color'] as Color).withOpacity(0.15),
                                shape: BoxShape.circle,
                              ),
                              child: Center(
                                child: Text(
                                  p['initials'] as String,
                                  style: GoogleFonts.poppins(color: p['color'] as Color, fontWeight: FontWeight.bold, fontSize: 16),
                                ),
                              ),
                            ),
                            const Spacer(),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(color: Colors.amber[50], borderRadius: BorderRadius.circular(8)),
                              child: Row(
                                children: [
                                  const Icon(Icons.star, color: Colors.amber, size: 14),
                                  const SizedBox(width: 4),
                                  Text(p['rating'] as String, style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text(
                          p['name'] as String,
                          style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 16, color: const Color(0xFF0A2463)),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          p['service'] as String,
                          style: GoogleFonts.poppins(color: Colors.grey[500], fontSize: 13),
                        ),
                        const Spacer(),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  p['price'] as String,
                                  style: GoogleFonts.poppins(color: const Color(0xFF2E7D32), fontWeight: FontWeight.bold, fontSize: 15),
                                ),
                                Text(
                                  p['distance'] as String,
                                  style: GoogleFonts.poppins(color: Colors.grey[400], fontSize: 12),
                                ),
                              ],
                            ),
                            ElevatedButton(
                              onPressed: () {
                                Navigator.push(context, MaterialPageRoute(builder: (context) => const ProviderResultsScreen()));
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFFF6B35),
                                foregroundColor: Colors.white,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                elevation: 0,
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                              ),
                              child: Text('Book Now', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 12)),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFooter(bool isMobile) {
    return Container(
      width: double.infinity,
      color: const Color(0xFF0A2463),
      padding: EdgeInsets.symmetric(vertical: 40, horizontal: isMobile ? 20 : 60),
      child: Column(
        children: [
          Text('KaamYaar AI ⚡', style: GoogleFonts.poppins(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text('Pakistan ka Smart Service Platform', style: GoogleFonts.poppins(color: Colors.white70, fontSize: 14)),
          const SizedBox(height: 40),
          const Divider(color: Colors.white24),
          const SizedBox(height: 20),
          Text('© 2026 KaamYaar AI. All rights reserved.', style: GoogleFonts.poppins(color: Colors.white.withOpacity(0.5), fontSize: 12)),
        ],
      ),
    );
  }
}
