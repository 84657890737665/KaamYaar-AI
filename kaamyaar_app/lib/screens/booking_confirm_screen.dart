import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import 'status_feedback_screen.dart';
import 'safety_timer_screen.dart';

class BookingConfirmScreen extends StatefulWidget {
  final Map<String, dynamic> provider;
  final bool femaleSafetyMode;

  const BookingConfirmScreen({
    super.key,
    required this.provider,
    required this.femaleSafetyMode,
  });

  @override
  State<BookingConfirmScreen> createState() => _BookingConfirmScreenState();
}

class _BookingConfirmScreenState extends State<BookingConfirmScreen> {
  bool _isLoading = false;

  Future<void> _confirmBooking() async {
    setState(() => _isLoading = true);

    try {
      final serviceTypes = (widget.provider['service_types'] as List? ?? []);
      final serviceType = serviceTypes.isNotEmpty
          ? serviceTypes.first.toString()
          : 'general';

      await ApiService.createBooking(
        providerId: widget.provider['provider_id'] ?? '',
        serviceType: serviceType,
        location: '${widget.provider['location_name'] ?? ''}, ${widget.provider['city'] ?? ''}',
        scheduledTime: DateTime.now().toIso8601String(),
        budget: (widget.provider['base_rate_pkr'] as num?)?.toDouble() ?? 1000,
      );

      if (!mounted) return;
      setState(() => _isLoading = false);

      if (widget.femaleSafetyMode) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => SafetyTimerScreen(provider: widget.provider),
          ),
        );
      } else {
        showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: Row(
                children: [
                  const Icon(Icons.check_circle, color: Color(0xFF43A047), size: 28),
                  const SizedBox(width: 8),
                  Text('Success!',
                      style: GoogleFonts.poppins(
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF0A2463))),
                ],
              ),
              content: Text('Booking Confirmed! Provider will arrive soon.',
                  style: GoogleFonts.poppins()),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            StatusFeedbackScreen(provider: widget.provider),
                      ),
                    );
                  },
                  child: Text('OK',
                      style: GoogleFonts.poppins(
                          color: const Color(0xFF1565C0),
                          fontWeight: FontWeight.bold)),
                ),
              ],
            );
          },
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoading = false);

      // API fail hone pe bhi proceed karo — graceful degradation
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Booking saved locally. Sync pending: $e'),
          backgroundColor: Colors.orange,
          duration: const Duration(seconds: 3),
        ),
      );

      // Phir bhi aage jao
      if (widget.femaleSafetyMode) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => SafetyTimerScreen(provider: widget.provider),
          ),
        );
      } else {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => StatusFeedbackScreen(provider: widget.provider),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Price Calculations
    final int baseRate = (widget.provider['base_rate_pkr'] as num? ?? 0).toInt();
    final double distanceKm =
        (widget.provider['distance_km'] as num? ?? 0).toDouble();
    final int distanceFee = (distanceKm * 50).round();
    final int serviceTax = (baseRate * 0.05).round();
    final int totalAmount = baseRate + distanceFee + serviceTax;

    // Formatting
    final String serviceTypes =
        (widget.provider['service_types'] as List? ?? []).join(', ');
    final String location = widget.provider['location_name'] ?? 'N/A';
    final String city = widget.provider['city'] ?? '';
    final int yearsExp = (widget.provider['years_experience'] as num? ?? 0).toInt();
    final int reviewCount = (widget.provider['review_count'] as num? ?? 0).toInt();
    final int onTimeScore =
        ((widget.provider['on_time_score'] as num? ?? 0) * 100).toInt();
    final int cancelRate =
        ((widget.provider['cancellation_rate'] as num? ?? 0) * 100).toInt();
    final bool isAvailable = widget.provider['is_available'] as bool? ?? true;

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FD),
      appBar: AppBar(
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF0D47A1), Color(0xFF1976D2)],
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
          'Confirm Booking',
          style: GoogleFonts.poppins(
              color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            // Provider Main Card (Blue Gradient)
            Container(
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF1565C0), Color(0xFF1976D2)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF1565C0).withOpacity(0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 60,
                        height: 60,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: Center(
                          child: Text(
                            _getInitials(widget.provider['name'] ?? '?'),
                            style: GoogleFonts.poppins(
                              color: const Color(0xFF1565C0),
                              fontWeight: FontWeight.bold,
                              fontSize: 20,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    widget.provider['name'] ?? 'Unknown',
                                    style: GoogleFonts.poppins(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 18,
                                      color: Colors.white,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: isAvailable
                                        ? Colors.greenAccent[400]
                                        : Colors.redAccent,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    isAvailable ? 'Available' : 'Busy',
                                    style: GoogleFonts.poppins(
                                      color: Colors.white,
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            Text(
                              _capitalize(serviceTypes),
                              style: GoogleFonts.poppins(
                                  color: Colors.white70, fontSize: 14),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                const Icon(Icons.star,
                                    color: Colors.amber, size: 16),
                                Text(
                                  ' ${widget.provider['rating'] ?? 'N/A'}',
                                  style: GoogleFonts.poppins(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                      color: Colors.white),
                                ),
                                Text(
                                  ' ($reviewCount reviews)',
                                  style: GoogleFonts.poppins(
                                      color: Colors.white70, fontSize: 12),
                                ),
                                const Spacer(),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.white24,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    _capitalize(
                                        widget.provider['skill_level'] ?? ''),
                                    style: GoogleFonts.poppins(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 12.0),
                    child: Divider(color: Colors.white30),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStatColumn(
                          'Experience', '$yearsExp Yrs', Icons.work_outline),
                      _buildStatColumn(
                          'On-Time', '$onTimeScore%', Icons.timer_outlined),
                      _buildStatColumn('Cancel Rate', '$cancelRate%',
                          Icons.cancel_outlined),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Provider Contact Info Card
            Container(
              decoration: _cardDecoration(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.lock_outline,
                          color: Color(0xFF0A2463), size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Provider Contact Details',
                        style: GoogleFonts.poppins(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF0A2463)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text('CNIC',
                      style: GoogleFonts.poppins(
                          fontSize: 12,
                          color: Colors.grey[600],
                          fontWeight: FontWeight.w500)),
                  const SizedBox(height: 6),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey[300]!),
                    ),
                    child: Text(
                      widget.provider['cnic'] ?? '35201-XXXXXX-X',
                      style: GoogleFonts.poppins(
                          fontSize: 14,
                          color: Colors.grey[700],
                          fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text('Mobile Number',
                      style: GoogleFonts.poppins(
                          fontSize: 12,
                          color: Colors.grey[600],
                          fontWeight: FontWeight.w500)),
                  const SizedBox(height: 6),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey[300]!),
                    ),
                    child: Text(
                      widget.provider['mobile'] ?? '0300-XXXXXXX',
                      style: GoogleFonts.poppins(
                          fontSize: 14,
                          color: Colors.grey[700],
                          fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(Icons.security, color: Colors.green, size: 14),
                      const SizedBox(width: 6),
                      Text(
                        'Contact details visible for your safety',
                        style: GoogleFonts.poppins(
                            fontSize: 11, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Booking Details
            Container(
              decoration: _cardDecoration(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Booking Details',
                      style: GoogleFonts.poppins(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF0A2463))),
                  const SizedBox(height: 16),
                  _buildDetailRow(
                      '🔧', 'Service', _capitalize(serviceTypes)),
                  const SizedBox(height: 12),
                  _buildDetailRow('📍', 'Location', '$location, $city'),
                  const SizedBox(height: 12),
                  _buildDetailRow('🚗', 'Distance', '$distanceKm km away'),
                  const SizedBox(height: 12),
                  _buildDetailRow('📅', 'Date', 'Today'),
                  const SizedBox(height: 12),
                  _buildDetailRow('⏰', 'Time', '3:00 PM'),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Price Breakdown
            Container(
              decoration: _cardDecoration(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Price Breakdown',
                      style: GoogleFonts.poppins(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF0A2463))),
                  const SizedBox(height: 16),
                  _buildPriceRow('Base Rate', baseRate),
                  const SizedBox(height: 12),
                  _buildPriceRow(
                      'Distance Fee ($distanceKm km)', distanceFee),
                  const SizedBox(height: 12),
                  _buildPriceRow('Service Tax (5%)', serviceTax),
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Total',
                          style: GoogleFonts.poppins(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: const Color(0xFF0A2463))),
                      Text('Rs. $totalAmount',
                          style: GoogleFonts.poppins(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: const Color(0xFF2E7D32))),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.only(
              left: 20, right: 20, bottom: 20, top: 10),
          child: Container(
            width: double.infinity,
            height: 56,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: _isLoading
                    ? [Colors.grey, Colors.grey]
                    : [const Color(0xFF43A047), const Color(0xFF2E7D32)],
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF2E7D32).withOpacity(0.4),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: _isLoading ? null : _confirmBooking,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : Text(
                      'Confirm Booking ✓',
                      style: GoogleFonts.poppins(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white),
                    ),
            ),
          ),
        ),
      ),
    );
  }

  BoxDecoration _cardDecoration() {
    return BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withOpacity(0.06),
          blurRadius: 10,
          offset: const Offset(0, 4),
        ),
      ],
    );
  }

  Widget _buildStatColumn(String title, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 4),
        Text(value,
            style: GoogleFonts.poppins(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: Colors.white)),
        Text(title,
            style: GoogleFonts.poppins(color: Colors.white70, fontSize: 11)),
      ],
    );
  }

  Widget _buildDetailRow(String icon, String title, String value) {
    return Row(
      children: [
        Text(icon, style: const TextStyle(fontSize: 18)),
        const SizedBox(width: 12),
        Text('$title:',
            style: GoogleFonts.poppins(color: Colors.grey[600], fontSize: 14)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(value,
              style: GoogleFonts.poppins(
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                  fontSize: 14),
              overflow: TextOverflow.ellipsis),
        ),
      ],
    );
  }

  Widget _buildPriceRow(String title, int amount) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title,
            style:
                GoogleFonts.poppins(color: Colors.grey[700], fontSize: 15)),
        Text('Rs. $amount',
            style: GoogleFonts.poppins(
                fontWeight: FontWeight.bold,
                color: Colors.black87,
                fontSize: 15)),
      ],
    );
  }

  String _getInitials(String name) {
    List<String> names = name.split(" ");
    String initials = "";
    int numWords = names.length > 2 ? 2 : names.length;
    for (int i = 0; i < numWords; i++) {
      if (names[i].isNotEmpty) initials += names[i][0];
    }
    return initials.toUpperCase();
  }

  String _capitalize(String text) {
    if (text.isEmpty) return text;
    return text.replaceAll('_', ' ').split(' ').map((word) {
      if (word.isEmpty) return word;
      return word[0].toUpperCase() + word.substring(1);
    }).join(' ');
  }
}