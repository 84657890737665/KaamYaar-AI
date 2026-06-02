import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../widgets/verified_badge.dart';
import 'status_feedback_screen.dart';
import 'warning_alert_screen.dart';

class SafetyTimerScreen extends StatefulWidget {
  final Map<String, dynamic> provider;
  
  const SafetyTimerScreen({super.key, required this.provider});

  @override
  State<SafetyTimerScreen> createState() => _SafetyTimerScreenState();
}

class _SafetyTimerScreenState extends State<SafetyTimerScreen> with SingleTickerProviderStateMixin {
  int _timeLeft = 45 * 60; // 45 minutes in seconds
  Timer? _timer;
  bool _isTimeExceeded = false;
  late AnimationController _shakeController;

  @override
  void initState() {
    super.initState();
    _shakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_timeLeft > 0) {
        setState(() {
          _timeLeft--;
        });
      } else {
        _timer?.cancel();
        if (!_isTimeExceeded) {
          setState(() {
            _isTimeExceeded = true;
          });
          _shakeController.repeat();
        }
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _shakeController.dispose();
    super.dispose();
  }

  String get _formattedTime {
    int minutes = _timeLeft ~/ 60;
    int seconds = _timeLeft % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
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
          'Safety Timer',
          style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        actions: [
          _buildBlinkingDot(),
          const SizedBox(width: 16),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            if (_isTimeExceeded) _buildWarningBanner(),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 600),
                  child: Column(
                    children: [
                      const SizedBox(height: 20),
                      _buildTimerSection(),
                      const SizedBox(height: 32),
                      _buildBookingStatusCard(),
                      const SizedBox(height: 32),
                      _buildActionButtons(context),
                      const SizedBox(height: 24),
                      Text(
                        'Your trusted contact is monitoring this booking',
                        style: GoogleFonts.poppins(color: Colors.grey[500], fontSize: 12),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 40),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBlinkingDot() {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0.0, end: 1.0),
      duration: const Duration(seconds: 1),
      builder: (context, value, child) {
        return Opacity(
          opacity: (sin(value * pi * 2) + 1.0) / 2.0, // Blinks continually
          child: Container(
            width: 12,
            height: 12,
            decoration: const BoxDecoration(
              color: Colors.redAccent,
              shape: BoxShape.circle,
            ),
          ),
        );
      },
      onEnd: () {
        // Since TweenAnimationBuilder doesn't loop easily, we use a simple state trick.
        setState(() {}); 
      },
    );
  }

  Widget _buildWarningBanner() {
    return AnimatedBuilder(
      animation: _shakeController,
      builder: (context, child) {
        final sineValue = sin(_shakeController.value * 2 * pi * 4); // 4 shakes per 500ms
        return Transform.translate(
          offset: Offset(sineValue * 10, 0),
          child: Container(
            width: double.infinity,
            color: const Color(0xFFD32F2F),
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.warning, color: Colors.white),
                const SizedBox(width: 8),
                Text(
                  '⚠️ Time exceeded! Are you okay?',
                  style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTimerSection() {
    return Column(
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            SizedBox(
              width: 240,
              height: 240,
              child: CircularProgressIndicator(
                value: _timeLeft / (45 * 60),
                strokeWidth: 12,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation<Color>(
                  _isTimeExceeded ? const Color(0xFFD32F2F) : const Color(0xFFAD1457),
                ),
              ),
            ),
            Container(
              width: 200,
              height: 200,
              decoration: const BoxDecoration(
                color: Color(0xFF0A2463), // Dark blue background as requested
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      _formattedTime,
                      style: GoogleFonts.poppins(
                        color: _isTimeExceeded ? Colors.redAccent : Colors.white,
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'min   sec',
                      style: GoogleFonts.poppins(color: Colors.white70, fontSize: 14),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Text(
          'Estimated completion time',
          style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14),
        ),
      ],
    );
  }

  Widget _buildBookingStatusCard() {
    final String serviceTypes = (widget.provider['service_types'] as List).join(', ');

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
          Row(
            children: [
              Expanded(
                child: Text(
                  widget.provider['name'],
                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0A2463)),
                ),
              ),
              const VerifiedBadge(),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            _capitalize(serviceTypes),
            style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14),
          ),
          const Divider(height: 32),
          _statusRow('Start Time', '10:00 AM'),
          const SizedBox(height: 8),
          _statusRow('Expected End', '10:45 AM'),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('🔵 '),
                Text(
                  'Work In Progress',
                  style: GoogleFonts.poppins(color: const Color(0xFF1565C0), fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _statusRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14)),
        Text(value, style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: Colors.black87, fontSize: 14)),
      ],
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Column(
      children: [
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [Color(0xFF2E7D32), Color(0xFF43A047)]),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(color: const Color(0xFF2E7D32).withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4)),
            ],
          ),
          child: ElevatedButton.icon(
            onPressed: () {
              _timer?.cancel();
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  title: Text('Safety Confirmed', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFF2E7D32))),
                  content: Text('Great! Booking marked as completed safely.', style: GoogleFonts.poppins()),
                  actions: [
                    TextButton(
                      onPressed: () {
                        Navigator.pop(context); // Close dialog
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(builder: (context) => StatusFeedbackScreen(provider: widget.provider)),
                        );
                      },
                      child: Text('Continue', style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: const Color(0xFF2E7D32))),
                    ),
                  ],
                ),
              );
            },
            icon: const Icon(Icons.check_circle, color: Colors.white),
            label: Text("I'm Safe ✓", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [Color(0xFFD32F2F), Color(0xFFE53935)]),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(color: const Color(0xFFD32F2F).withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4)),
            ],
          ),
          child: ElevatedButton.icon(
            onPressed: () async {
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => WarningAlertScreen(provider: widget.provider),
                ),
              );
              if (result == 'extend') {
                setState(() {
                  _timeLeft += 15 * 60;
                  _isTimeExceeded = false;
                });
                _shakeController.reset();
                _shakeController.stop();
                _startTimer();
              }
            },
            icon: const Icon(Icons.warning_amber_rounded, color: Colors.white),
            label: Text("🚨 Send Alert", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
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

// Dummy Warning Alert Screen placeholder
class DummyWarningAlertScreen extends StatelessWidget {
  const DummyWarningAlertScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Emergency Alert"),
        backgroundColor: const Color(0xFFD32F2F),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.local_police, color: Color(0xFFD32F2F), size: 100),
            const SizedBox(height: 20),
            Text(
              "Authorities & Trusted Contacts\nhave been notified.",
              textAlign: TextAlign.center,
              style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
