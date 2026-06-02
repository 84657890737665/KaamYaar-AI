import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'provider_home_screen.dart';
import 'login_screen.dart';


class ProviderRegistrationScreen extends StatefulWidget {
  const ProviderRegistrationScreen({super.key});

  @override
  State<ProviderRegistrationScreen> createState() => _ProviderRegistrationScreenState();
}

class _ProviderRegistrationScreenState extends State<ProviderRegistrationScreen> {
  // Mock state for uploaded images
  bool _hasCnicFront = false;
  bool _hasCnicBack = false;
  bool _hasSelfie = false;

  // Toggle state for new vs returning user
  bool _isReturningUser = false;

  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _cnicController = TextEditingController();
  final TextEditingController _mobileController = TextEditingController();
  final TextEditingController _experienceController = TextEditingController();
  final TextEditingController _addressController = TextEditingController();

  final FocusNode _nameFocus = FocusNode();
  final FocusNode _cnicFocus = FocusNode();
  final FocusNode _mobileFocus = FocusNode();
  final FocusNode _expFocus = FocusNode();
  final FocusNode _addressFocus = FocusNode();

  final List<String> _selectedServices = [];
  final List<String> _availableServices = [
    'AC', 'Plumber', 'Cook', 'Beautician', 'Carpenter', 'Electrician',
    'Painter', 'Mechanic', 'Driver', 'Mason', 'Cleaner', 'Tutor'
  ];

  @override
  void initState() {
    super.initState();
    // Start completely empty for new user
    _hasCnicFront = false;
    _hasCnicBack = false;
    _hasSelfie = false;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _cnicController.dispose();
    _mobileController.dispose();
    _experienceController.dispose();
    _addressController.dispose();

    _nameFocus.dispose();
    _cnicFocus.dispose();
    _mobileFocus.dispose();
    _expFocus.dispose();
    _addressFocus.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(kToolbarHeight),
        child: Container(
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(color: Color(0xFFE2E8F0), width: 1),
            ),
          ),
          child: AppBar(
            backgroundColor: Colors.white,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Color(0xFF0F172A)),
              onPressed: () => Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
              ),
            ),
            title: Text(
              'Provider Registration',
              style: GoogleFonts.inter(color: const Color(0xFF0F172A), fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ),
        ),
      ),
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 600),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  _buildTopInfoCard(),
                  const SizedBox(height: 16),
                  _buildUserTypeToggle(),
                  const SizedBox(height: 24),
                  _buildRegistrationForm(),
                  const SizedBox(height: 24),
                  _buildCnicCard(
                    title: 'CNIC Front',
                    subtitle: 'Upload front side of your CNIC',
                    hasImage: _hasCnicFront,
                    onCameraTap: () => setState(() => _hasCnicFront = true),
                    onGalleryTap: () => setState(() => _hasCnicFront = true),
                  ),
                  const SizedBox(height: 24),
                  _buildCnicCard(
                    title: 'CNIC Back',
                    subtitle: 'Upload back side of your CNIC',
                    hasImage: _hasCnicBack,
                    onCameraTap: () => setState(() => _hasCnicBack = true),
                    onGalleryTap: () => setState(() => _hasCnicBack = true),
                  ),
                  const SizedBox(height: 24),
                  _buildSelfieCard(),
                  const SizedBox(height: 32),
                  _buildVerificationBadge(),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ),
      ),
      bottomNavigationBar: _buildSubmitButton(),
    );
  }

  Widget _buildTopInfoCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF4F46E5), Color(0xFF6366F1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF4338CA), width: 1),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.security, color: Colors.white, size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _isReturningUser ? 'Welcome Back to KaamYaar! 👋' : 'Welcome to KaamYaar! 👋',
                  style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
                ),
                const SizedBox(height: 6),
                Text(
                  _isReturningUser
                      ? 'Apna registered Mobile aur CNIC dakhil karein'
                      : 'Apni details fill karein aur verify hojayein',
                  style: GoogleFonts.inter(color: Colors.white.withOpacity(0.9), fontSize: 13, height: 1.4),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUserTypeToggle() {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
      ),
      child: Row(
        children: [
          Expanded(
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _isReturningUser = false;
                  // Clear fields and files for new user registration
                  _nameController.clear();
                  _cnicController.clear();
                  _mobileController.clear();
                  _experienceController.clear();
                  _addressController.clear();
                  _selectedServices.clear();
                  _hasCnicFront = false;
                  _hasCnicBack = false;
                  _hasSelfie = false;
                });
              },
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: !_isReturningUser ? Colors.white : Colors.transparent,
                  borderRadius: BorderRadius.circular(6),
                  border: !_isReturningUser ? Border.all(color: const Color(0xFFE2E8F0)) : null,
                  boxShadow: !_isReturningUser
                      ? [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ]
                      : null,
                ),
                child: Center(
                  child: Text(
                    'Naya Provider',
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      fontWeight: !_isReturningUser ? FontWeight.w600 : FontWeight.w400,
                      color: !_isReturningUser ? const Color(0xFF4F46E5) : const Color(0xFF64748B),
                    ),
                  ),
                ),
              ),
            ),
          ),
          Expanded(
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _isReturningUser = true;
                  // Autofill mock details for returning partner
                  _nameController.text = 'Ali Hassan';
                  _cnicController.text = '35201-1234567-1';
                  _mobileController.text = '0300-1234567';
                  _experienceController.text = '5';
                  _addressController.text = 'G-13, Islamabad';
                  _selectedServices.clear();
                  _selectedServices.addAll(['AC', 'Plumber', 'Electrician']);
                  _hasCnicFront = true;
                  _hasCnicBack = true;
                  _hasSelfie = true;
                });
              },
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: _isReturningUser ? Colors.white : Colors.transparent,
                  borderRadius: BorderRadius.circular(6),
                  border: _isReturningUser ? Border.all(color: const Color(0xFFE2E8F0)) : null,
                  boxShadow: _isReturningUser
                      ? [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ]
                      : null,
                ),
                child: Center(
                  child: Text(
                    'Purana Partner',
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      fontWeight: _isReturningUser ? FontWeight.w600 : FontWeight.w400,
                      color: _isReturningUser ? const Color(0xFF4F46E5) : const Color(0xFF64748B),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRegistrationForm() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Provider Information',
            style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.bold, color: const Color(0xFF0F172A)),
          ),
          const SizedBox(height: 16),

          // Full Name
          TextField(
            controller: _nameController,
            focusNode: _nameFocus,
            autofocus: false,
            enableInteractiveSelection: true,
            keyboardType: TextInputType.name,
            style: GoogleFonts.inter(color: const Color(0xFF0F172A), fontSize: 14),
            decoration: InputDecoration(
              labelText: 'Full Name',
              labelStyle: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 13),
              hintText: 'Ali Hassan',
              hintStyle: GoogleFonts.inter(color: const Color(0xFF94A3B8), fontSize: 13),
              prefixIcon: const Icon(Icons.person, color: Color(0xFF64748B), size: 20),
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF4F46E5), width: 1.5),
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 16),

          // CNIC Number
          TextField(
            controller: _cnicController,
            focusNode: _cnicFocus,
            autofocus: false,
            enableInteractiveSelection: true,
            keyboardType: TextInputType.number,
            style: GoogleFonts.inter(color: const Color(0xFF0F172A), fontSize: 14),
            decoration: InputDecoration(
              labelText: 'CNIC Number',
              labelStyle: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 13),
              hintText: '35201-1234567-1',
              hintStyle: GoogleFonts.inter(color: const Color(0xFF94A3B8), fontSize: 13),
              prefixIcon: const Icon(Icons.badge, color: Color(0xFF64748B), size: 20),
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF4F46E5), width: 1.5),
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 16),

          // Mobile Number
          TextField(
            controller: _mobileController,
            focusNode: _mobileFocus,
            autofocus: false,
            enableInteractiveSelection: true,
            keyboardType: TextInputType.phone,
            style: GoogleFonts.inter(color: const Color(0xFF0F172A), fontSize: 14),
            decoration: InputDecoration(
              labelText: 'Mobile Number',
              labelStyle: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 13),
              hintText: '0300-1234567',
              hintStyle: GoogleFonts.inter(color: const Color(0xFF94A3B8), fontSize: 13),
              prefixIcon: const Icon(Icons.phone, color: Color(0xFF64748B), size: 20),
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF4F46E5), width: 1.5),
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 16),

          // Years of Experience
          TextField(
            controller: _experienceController,
            focusNode: _expFocus,
            autofocus: false,
            enableInteractiveSelection: true,
            keyboardType: TextInputType.number,
            style: GoogleFonts.inter(color: const Color(0xFF0F172A), fontSize: 14),
            decoration: InputDecoration(
              labelText: 'Years of Experience',
              labelStyle: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 13),
              hintText: '5',
              hintStyle: GoogleFonts.inter(color: const Color(0xFF94A3B8), fontSize: 13),
              prefixIcon: const Icon(Icons.work, color: Color(0xFF64748B), size: 20),
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF4F46E5), width: 1.5),
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 16),

          // Address
          TextField(
            controller: _addressController,
            focusNode: _addressFocus,
            autofocus: false,
            enableInteractiveSelection: true,
            keyboardType: TextInputType.streetAddress,
            style: GoogleFonts.inter(color: const Color(0xFF0F172A), fontSize: 14),
            decoration: InputDecoration(
              labelText: 'Address',
              labelStyle: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 13),
              hintText: 'G-13, Islamabad',
              hintStyle: GoogleFonts.inter(color: const Color(0xFF94A3B8), fontSize: 13),
              prefixIcon: const Icon(Icons.location_on, color: Color(0xFF64748B), size: 20),
              filled: true,
              fillColor: const Color(0xFFF8FAFC),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFF4F46E5), width: 1.5),
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(height: 20),

          // Services Offered (MultiSelect Chips)
          Text(
            'Services Offered (Select Multiple)',
            style: GoogleFonts.inter(fontSize: 13, color: const Color(0xFF64748B), fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8.0,
            runSpacing: 8.0,
            children: _availableServices.map((service) {
              final isSelected = _selectedServices.contains(service);
              return FilterChip(
                label: Text(
                  service,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: isSelected ? const Color(0xFF4F46E5) : const Color(0xFF475569),
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                  ),
                ),
                selected: isSelected,
                selectedColor: const Color(0xFFEEF2FF),
                checkmarkColor: const Color(0xFF4F46E5),
                backgroundColor: const Color(0xFFF1F5F9),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                  side: BorderSide(
                    color: isSelected ? const Color(0xFF6366F1) : const Color(0xFFE2E8F0),
                    width: 1,
                  ),
                ),
                onSelected: (bool selected) {
                  setState(() {
                    if (selected) {
                      _selectedServices.add(service);
                    } else {
                      _selectedServices.remove(service);
                    }
                  });
                },
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildCnicCard({
    required String title,
    required String subtitle,
    required bool hasImage,
    required VoidCallback onCameraTap,
    required VoidCallback onGalleryTap,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 16, color: const Color(0xFF0F172A))),
          const SizedBox(height: 4),
          Text(subtitle, style: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 13)),
          const SizedBox(height: 20),
          Center(
            child: Container(
              width: 200,
              height: 130,
              decoration: BoxDecoration(
                color: hasImage ? const Color(0xFFECFDF5) : const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: hasImage ? const Color(0xFF10B981) : const Color(0xFFE2E8F0),
                  width: 1.5,
                  style: BorderStyle.solid,
                ),
              ),
              child: hasImage
                  ? Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 36),
                        const SizedBox(height: 8),
                        Text('Image Uploaded', style: GoogleFonts.inter(color: const Color(0xFF047857), fontWeight: FontWeight.w600, fontSize: 13)),
                      ],
                    )
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.camera_alt_outlined, color: const Color(0xFF94A3B8), size: 36),
                        const SizedBox(height: 8),
                        Text('Tap to upload', style: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 12)),
                      ],
                    ),
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: onCameraTap,
                  icon: const Text('📷', style: TextStyle(fontSize: 14)),
                  label: Text('Camera', style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 13)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF4F46E5),
                    elevation: 0,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: onGalleryTap,
                  icon: const Text('🖼️', style: TextStyle(fontSize: 14)),
                  label: Text('Gallery', style: GoogleFonts.inter(color: const Color(0xFF0F172A), fontWeight: FontWeight.w600, fontSize: 13)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFF1F5F9),
                    elevation: 0,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSelfieCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Live Selfie Verification', style: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 16, color: const Color(0xFF0F172A))),
          const SizedBox(height: 4),
          Text('Take a clear selfie for face verification', style: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 13)),
          const SizedBox(height: 20),
          Center(
            child: Container(
              width: 150,
              height: 150,
              decoration: BoxDecoration(
                color: _hasSelfie ? const Color(0xFFECFDF5) : const Color(0xFFF8FAFC),
                shape: BoxShape.circle,
                border: Border.all(
                  color: _hasSelfie ? const Color(0xFF10B981) : const Color(0xFFE2E8F0),
                  width: 1.5,
                ),
              ),
              child: _hasSelfie
                  ? Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.face_retouching_natural, color: Color(0xFF10B981), size: 44),
                        const SizedBox(height: 8),
                        Text('Captured', style: GoogleFonts.inter(color: const Color(0xFF047857), fontWeight: FontWeight.w600, fontSize: 13)),
                      ],
                    )
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.face, color: const Color(0xFF94A3B8), size: 44),
                      ],
                    ),
            ),
          ),
          const SizedBox(height: 24),
          Center(
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF4F46E5), Color(0xFF6366F1)],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: ElevatedButton.icon(
                onPressed: () => setState(() => _hasSelfie = true),
                icon: const Text('📸', style: TextStyle(fontSize: 15)),
                label: Text('Take Selfie', style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVerificationBadge() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFFFEF3C7),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: const Color(0xFFFDE68A)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('⏳', style: TextStyle(fontSize: 14)),
              const SizedBox(width: 8),
              Text(
                'Verification Pending',
                style: GoogleFonts.inter(color: const Color(0xFFB45309), fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'We will verify within 24 hours',
          style: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildSubmitButton() {
    return SafeArea(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(
            top: BorderSide(color: Color(0xFFE2E8F0), width: 1),
          ),
        ),
        child: Container(
          width: double.infinity,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF4F46E5), Color(0xFF6366F1)],
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: ElevatedButton(
            onPressed: () {
              // Details fields validation
              if (_nameController.text.trim().isEmpty ||
                  _cnicController.text.trim().isEmpty ||
                  _mobileController.text.trim().isEmpty ||
                  _experienceController.text.trim().isEmpty ||
                  _addressController.text.trim().isEmpty) {
                showDialog(
                  context: context,
                  builder: (dialogContext) => AlertDialog(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    title: Row(
                      children: [
                        const Text('⚠️', style: TextStyle(fontSize: 20)),
                        const SizedBox(width: 8),
                        Text(
                          'Details Missing',
                          style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFFEF4444)),
                        ),
                      ],
                    ),
                    content: Text(
                      'Aapne apni mukammal maloomat fill nahi keen.\n\nBaraye meharbani:\n- Name\n- CNIC\n- Mobile Number\n- Experience\n- Address\n\nTamam maloomat dakhil karein.',
                      style: GoogleFonts.inter(height: 1.5, color: const Color(0xFF475569)),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(dialogContext),
                        child: Text(
                          'Theek Hai',
                          style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFFEF4444)),
                        ),
                      ),
                    ],
                  ),
                );
                return;
              }

              // Verification documents validation check (only for new users)
              if (!_isReturningUser && (!_hasCnicFront || !_hasCnicBack || !_hasSelfie)) {
                showDialog(
                  context: context,
                  builder: (dialogContext) => AlertDialog(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    title: Row(
                      children: [
                        const Text('⚠️', style: TextStyle(fontSize: 20)),
                        const SizedBox(width: 8),
                        Text(
                          'Documents Required',
                          style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFFF59E0B)),
                        ),
                      ],
                    ),
                    content: Text(
                      'Aapne verification documents upload nahi kiye.\n\nBaraye meharbani:\n1. CNIC Front\n2. CNIC Back\n3. Live Selfie\n\nTamam documents upload karna laazmi hai.',
                      style: GoogleFonts.inter(height: 1.5, color: const Color(0xFF475569)),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(dialogContext),
                        child: Text(
                          'Theek Hai',
                          style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFFF59E0B)),
                        ),
                      ),
                    ],
                  ),
                );
                return;
              }

              // All validations passed - show success dialogue
              showDialog(
                context: context,
                builder: (dialogContext) => AlertDialog(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  title: Text(
                    _isReturningUser ? 'Welcome Back!' : 'Success',
                    style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFF10B981)),
                  ),
                  content: Text(
                    _isReturningUser
                        ? 'Aapka account pehle se verified hai!\nDashboard par muntaqil ho rahe hain.'
                        : 'Aapki registration submit ho gayi hai!\nHum aapki details verify karenge.\nVerification complete hone par aapko app notification milegi.\nYeh process 24 hours mein complete hogi.',
                    style: GoogleFonts.inter(height: 1.5, color: const Color(0xFF475569)),
                  ),
                  actions: [
                    TextButton(
                      onPressed: () {
                        Navigator.pop(dialogContext); // close dialog
                        Navigator.pushReplacement(
                          context, // outer build context
                          MaterialPageRoute(
                            builder: (context) => ProviderHomeScreen(
                              name: _nameController.text.isNotEmpty ? _nameController.text : 'Ahmed Khan',
                              cnic: _cnicController.text.isNotEmpty ? _cnicController.text : '35201-1234567-1',
                              mobile: _mobileController.text.isNotEmpty ? _mobileController.text : '0300-1234567',
                              services: _selectedServices.isNotEmpty ? _selectedServices.join(', ') : 'General Services',
                              experience: _experienceController.text.isNotEmpty ? _experienceController.text : '5',
                              isVerified: _isReturningUser,
                            ),
                          ),
                        );
                      },
                      child: Text('OK', style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFF10B981))),
                    ),
                  ],
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: Text(
              _isReturningUser ? 'Login & View Dashboard →' : 'Submit for Verification →',
              style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
        ),
      ),
    );
  }
}
