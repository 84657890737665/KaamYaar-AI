import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class CallLogScreen extends StatelessWidget {
  const CallLogScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // 3 mock entries
    final List<Map<String, String>> mockCalls = [
      {
        'name': 'Ammi',
        'phone': '0300-1234567',
        'dateTime': 'Today, 02:30 PM',
        'status': 'Completed',
      },
      {
        'name': 'Bhai',
        'phone': '0312-9876543',
        'dateTime': 'Yesterday, 08:15 PM',
        'status': 'Missed',
      },
      {
        'name': 'Abbu',
        'phone': '0333-5551234',
        'dateTime': '18 May, 11:00 AM',
        'status': 'Completed',
      },
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FD),
      appBar: AppBar(
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFF0A2463), Color(0xFF1565C0)],
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
          'Call Log',
          style: GoogleFonts.poppins(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: mockCalls.length,
        itemBuilder: (context, index) {
          final call = mockCalls[index];
          final isCompleted = call['status'] == 'Completed';

          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.03),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              leading: CircleAvatar(
                backgroundColor: isCompleted
                    ? Colors.green.withOpacity(0.1)
                    : Colors.red.withOpacity(0.1),
                radius: 24,
                child: Icon(
                  isCompleted ? Icons.call_received : Icons.call_missed,
                  color: isCompleted ? Colors.green : Colors.red,
                ),
              ),
              title: Text(
                call['name']!,
                style: GoogleFonts.poppins(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: const Color(0xFF0A2463),
                ),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  Text(
                    call['phone']!,
                    style: GoogleFonts.poppins(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    call['dateTime']!,
                    style: GoogleFonts.poppins(
                      color: Colors.grey[400],
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: isCompleted
                      ? Colors.green.withOpacity(0.1)
                      : Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  call['status']!,
                  style: GoogleFonts.poppins(
                    color: isCompleted ? Colors.green : Colors.red,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
