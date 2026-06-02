import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import '../services/api_service.dart';
import 'provider_results_screen.dart';

class RequestInputScreen extends StatefulWidget {
  const RequestInputScreen({super.key});

  @override
  State<RequestInputScreen> createState() => _RequestInputScreenState();
}

class _RequestInputScreenState extends State<RequestInputScreen> {
  final TextEditingController _textController = TextEditingController();
  final stt.SpeechToText _speech = stt.SpeechToText();

  bool _isListening = false;
  bool _isLoading = false;
  String _loadingStep = '';
  Map<String, dynamic>? _parsedResult;

  // Example prompts to help user
  final List<String> _examplePrompts = [
    'AC kharab hai, kal subah 10 baje, G-23 Islamabad',
    'Plumber chahiye aaj shaam 5 baje, DHA Karachi, budget 2000',
    'بجلی کا مسئلہ ہے، فوری چاہیے، گلبرگ لاہور',
    'Cook book karni hai Sunday lunch ke liye, F-7 Islamabad',
    'AC repair urgent, Phase 5 DHA Karachi, flexible budget',
  ];

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _startListening() async {
    bool available = await _speech.initialize();
    if (available) {
      setState(() => _isListening = true);
      _speech.listen(
        onResult: (result) {
          setState(() {
            _textController.text = result.recognizedWords;
          });
        },
        localeId: 'ur_PK',
      );
    }
  }

  void _stopListening() {
    _speech.stop();
    setState(() => _isListening = false);
  }

  Future<void> _processRequest() async {
    final text = _textController.text.trim();
    if (text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pehle apni zaroorat likho ya bolo!')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _loadingStep = 'Aapki baat samajh raha hun...';
      _parsedResult = null;
    });

    try {
      // Step 1: Parse request
      final parsed = await ApiService.parseRequest(rawText: text);
      setState(() {
        _parsedResult = parsed;
        _loadingStep = 'Service providers dhundh raha hun...';
      });

      // Extract fields from parsed response
      final serviceType = parsed['service_type'] ??
          parsed['parsed_request']?['service_type'] ??
          'general';
      final location = parsed['location'] ??
          parsed['parsed_request']?['location'] ??
          'Pakistan';
      final budget = (parsed['budget'] ??
              parsed['parsed_request']?['budget'] ??
              2000)
          .toDouble();

      // Step 2: Find providers
      List<dynamic> providers = [];
      try {
        providers = await ApiService.findProviders(
          serviceType: serviceType.toString(),
          location: location.toString(),
          budget: budget,
        );
      } catch (_) {}

      setState(() => _loadingStep = 'Best providers rank kar raha hun...');

      // Step 3: Rank providers
      if (providers.isNotEmpty) {
        try {
          providers = await ApiService.rankProviders(
            providers: providers,
            serviceType: serviceType.toString(),
            location: location.toString(),
            budget: budget,
          );
        } catch (_) {}
      }

      if (!mounted) return;
      setState(() => _isLoading = false);

      // Navigate to results
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ProviderResultsScreen(
            providers: providers,
            serviceType: serviceType.toString(),
            location: location.toString(),
            budget: budget,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Kuch masla aaya: $e'),
          backgroundColor: Colors.red,
          action: SnackBarAction(
            label: 'Dobara Try',
            textColor: Colors.white,
            onPressed: _processRequest,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
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
          'KaamYaar AI',
          style: GoogleFonts.poppins(
              color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: _isLoading ? _buildLoadingView() : _buildInputView(),
    );
  }

  Widget _buildLoadingView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Animated AI brain icon
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF0D47A1), Color(0xFF1976D2)],
                ),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF1565C0).withOpacity(0.4),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: const Icon(Icons.psychology, color: Colors.white, size: 50),
            ),
            const SizedBox(height: 32),
            Text(
              _loadingStep,
              style: GoogleFonts.poppins(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF0A2463),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            const CircularProgressIndicator(color: Color(0xFF1565C0)),
            const SizedBox(height: 24),
            // Agent steps
            _buildAgentStep('🧠', 'Language Parser', _loadingStep.contains('samajh')),
            _buildAgentStep('🔍', 'Provider Discovery', _loadingStep.contains('dhundh')),
            _buildAgentStep('⭐', 'Ranking Engine', _loadingStep.contains('rank')),
          ],
        ),
      ),
    );
  }

  Widget _buildAgentStep(String emoji, String label, bool active) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 20)),
          const SizedBox(width: 12),
          Text(
            label,
            style: GoogleFonts.poppins(
              fontSize: 14,
              fontWeight: active ? FontWeight.bold : FontWeight.normal,
              color: active ? const Color(0xFF1565C0) : Colors.grey,
            ),
          ),
          const SizedBox(width: 8),
          if (active)
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Color(0xFF1565C0),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInputView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),

          // Hero section
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0A2463), Color(0xFF1565C0)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Kya chahiye aapko? 🤖',
                  style: GoogleFonts.poppins(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Urdu, Roman Urdu, English ya koi bhi zaban mein batao — AI samjhega!',
                  style: GoogleFonts.poppins(
                    color: Colors.white70,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 12),
                // Language chips
                Wrap(
                  spacing: 8,
                  children: ['اردو', 'Roman Urdu', 'English', 'پنجابی', 'سندھی', 'پشتو']
                      .map((lang) => Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                  color: Colors.white.withOpacity(0.4)),
                            ),
                            child: Text(lang,
                                style: GoogleFonts.poppins(
                                    color: Colors.white, fontSize: 11)),
                          ))
                      .toList(),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Main input box
          Text(
            'Apni zaroorat likho:',
            style: GoogleFonts.poppins(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF0A2463),
            ),
          ),
          const SizedBox(height: 10),
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF1565C0).withOpacity(0.3)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: TextField(
              controller: _textController,
              maxLines: 4,
              style: GoogleFonts.poppins(fontSize: 15),
              decoration: InputDecoration(
                hintText:
                    'Misal: "AC kharab hai, kal subah 10 baje, G-23 Islamabad, budget 2000"\n\nYa Urdu mein: "بجلی کا مسئلہ ہے، فوری چاہیے"',
                hintStyle:
                    GoogleFonts.poppins(color: Colors.grey[400], fontSize: 13),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.all(16),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Voice button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: _isListening ? _stopListening : _startListening,
              style: OutlinedButton.styleFrom(
                side: BorderSide(
                  color: _isListening ? Colors.red : const Color(0xFF1565C0),
                  width: 2,
                ),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
              ),
              icon: Icon(
                _isListening ? Icons.stop : Icons.mic,
                color: _isListening ? Colors.red : const Color(0xFF1565C0),
              ),
              label: Text(
                _isListening ? 'Sunna band karo' : 'Voice se bolo 🎤',
                style: GoogleFonts.poppins(
                  color: _isListening ? Colors.red : const Color(0xFF1565C0),
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Example prompts
          Text(
            'Ya in mein se choose karo:',
            style: GoogleFonts.poppins(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF0A2463),
            ),
          ),
          const SizedBox(height: 12),
          ..._examplePrompts.map((prompt) => GestureDetector(
                onTap: () {
                  setState(() => _textController.text = prompt);
                },
                child: Container(
                  width: double.infinity,
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey[200]!),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.03),
                        blurRadius: 6,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      const Text('💬', style: TextStyle(fontSize: 16)),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          prompt,
                          style: GoogleFonts.poppins(
                            fontSize: 13,
                            color: Colors.black87,
                          ),
                        ),
                      ),
                      const Icon(Icons.arrow_forward_ios,
                          size: 14, color: Colors.grey),
                    ],
                  ),
                ),
              )),

          const SizedBox(height: 100),
        ],
      ),
    );
  }
}
