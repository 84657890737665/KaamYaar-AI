import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'status_feedback_screen.dart';
import 'call_initiated_screen.dart';

class WarningAlertScreen extends StatefulWidget {
  final Map<String, dynamic> provider;

  const WarningAlertScreen({super.key, required this.provider});

  @override
  State<WarningAlertScreen> createState() => _WarningAlertScreenState();
}

class _WarningAlertScreenState extends State<WarningAlertScreen> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 0.9, end: 1.15).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFFD32F2F),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFD32F2F), Color(0xFFB71C1C)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: MediaQuery.of(context).size.height -
                    MediaQuery.of(context).padding.top -
                    MediaQuery.of(context).padding.bottom -
                    40,
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const SizedBox(height: 20),
                  
                  // Pulse Warning Icon & Texts
                  Column(
                    children: [
                      ScaleTransition(
                        scale: _pulseAnimation,
                        child: const Icon(
                          Icons.warning_amber_rounded,
                          color: Colors.white,
                          size: 100,
                        ),
                      ),
                      const SizedBox(height: 24),
                      Text(
                        'KaamYaar Safety Alert',
                        style: GoogleFonts.poppins(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Service expected time guzar gayi hai.\nKya aap theek hain?',
                        style: GoogleFonts.poppins(
                          fontSize: 16,
                          color: Colors.white,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 40),
                  
                  // Stacked Action Buttons
                  Column(
                    children: [
                      // Button 1: Haan theek hoon
                      _buildGradientButton(
                        text: 'Haan, main theek hoon ✓',
                        colors: [const Color(0xFF2E7D32), const Color(0xFF43A047)],
                        onTap: () {
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                              title: Text(
                                'Safe',
                                style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFF2E7D32)),
                              ),
                              content: Text('Glad you are safe!', style: GoogleFonts.poppins()),
                              actions: [
                                TextButton(
                                  onPressed: () {
                                    Navigator.pop(context); // Close dialog
                                    Navigator.pushReplacement(
                                      context,
                                      MaterialPageRoute(
                                        builder: (context) => StatusFeedbackScreen(provider: widget.provider),
                                      ),
                                    );
                                  },
                                  child: Text(
                                    'OK',
                                    style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFF2E7D32)),
                                  ),
                                )
                              ],
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 16),
                      
                      // Button 2: Thoda aur waqt do
                      _buildGradientButton(
                        text: 'Thoda aur waqt chahiye',
                        colors: [const Color(0xFFFF6B35), const Color(0xFFFF8C42)],
                        onTap: () {
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                              title: Text(
                                'Time Extended',
                                style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFFFF6B35)),
                              ),
                              content: Text('Timer extended by 15 minutes', style: GoogleFonts.poppins()),
                              actions: [
                                TextButton(
                                  onPressed: () {
                                    Navigator.pop(context); // Close dialog
                                    Navigator.pop(context, 'extend'); // Pop back with extend flag
                                  },
                                  child: Text(
                                    'OK',
                                    style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFFFF6B35)),
                                  ),
                                )
                              ],
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 16),
                      
                      // Button 3: Help chahiye — Alert bhejo
                      _buildSolidButton(
                        text: '⚠️ Help chahiye — Alert bhejo!',
                        color: const Color(0xFF7B0000),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const CallInitiatedScreen(
                                contactName: "Trusted Contact",
                                contactNumber: "0300-1234567",
                                callTranscript: "KaamYaar AI alert: Aapki family member ne safety alert bheja hai. Please confirm karo ke woh theek hain.",
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 40),
                  
                  // Bottom Safety Text
                  Text(
                    'Your trusted contact has been notified',
                    style: GoogleFonts.poppins(
                      fontSize: 12,
                      color: Colors.white60,
                      fontStyle: FontStyle.italic,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGradientButton({required String text, required List<Color> colors, required VoidCallback onTap}) {
    return Container(
      width: double.infinity,
      height: 56,
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: colors),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: colors[0].withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        child: Text(
          text,
          style: GoogleFonts.poppins(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ),
    );
  }

  Widget _buildSolidButton({required String text, required Color color, required VoidCallback onTap}) {
    return Container(
      width: double.infinity,
      height: 56,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        child: Text(
          text,
          style: GoogleFonts.poppins(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ),
    );
  }
}
