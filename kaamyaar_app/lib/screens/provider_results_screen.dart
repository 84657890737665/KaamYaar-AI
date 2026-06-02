import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'booking_confirm_screen.dart';
import '../widgets/verified_badge.dart';
import 'female_safety_booking_screen.dart';

class ProviderResultsScreen extends StatefulWidget {
  // API se aane wala data — optional, direct navigation ke liye
  final List<dynamic>? providers;
  final String? serviceType;
  final String? location;
  final double? budget;

  const ProviderResultsScreen({
    super.key,
    this.providers,
    this.serviceType,
    this.location,
    this.budget,
  });

  @override
  State<ProviderResultsScreen> createState() => _ProviderResultsScreenState();
}

class _ProviderResultsScreenState extends State<ProviderResultsScreen> {
  String _selectedFilter = 'All';
  String _searchQuery = '';
  bool _femaleSafetyMode = false;

  List<Map<String, dynamic>> _allProviders = [];
  bool _isLoading = true;

  final List<Map<String, String>> filters = [
    {'label': 'All', 'value': 'all'},
    {'label': 'AC', 'value': 'ac_technician'},
    {'label': 'Plumber', 'value': 'plumber'},
    {'label': 'Cook', 'value': 'cook'},
    {'label': 'Beautician', 'value': 'beautician'},
    {'label': 'Carpenter', 'value': 'carpenter'},
    {'label': 'Electrician', 'value': 'electrician'},
    {'label': 'Painter', 'value': 'painter'},
    {'label': 'Mechanic', 'value': 'mechanic'},
    {'label': 'Driver', 'value': 'driver'},
    {'label': 'Mason', 'value': 'mason'},
    {'label': 'Cleaner', 'value': 'cleaner'},
    {'label': 'Tutor', 'value': 'tutor'},
  ];

  final verifiedIds = [
    'PRV001', 'PRV003', 'PRV005', 'PRV007', 'PRV008', 'PRV009', 'PRV010',
    'PRV015', 'PRV018', 'PRV020', 'PRV022', 'PRV025', 'PRV027', 'PRV029'
  ];

  @override
  void initState() {
    super.initState();
    _loadProviders();
  }

  Future<void> _loadProviders() async {
    // Agar API se providers aaye hain toh unhe use karo
    if (widget.providers != null && widget.providers!.isNotEmpty) {
      setState(() {
        _allProviders = widget.providers!.map((e) {
          final provider = Map<String, dynamic>.from(e);
          provider['is_verified'] = verifiedIds.contains(provider['provider_id']);
          return provider;
        }).toList();
        _isLoading = false;
      });
      return;
    }

    // Fallback: JSON file se load karo (direct navigation ke liye)
    try {
      final String jsonString =
          await rootBundle.loadString('assets/data/providers.json');
      final List<dynamic> jsonList = json.decode(jsonString);
      setState(() {
        _allProviders = jsonList.map((e) {
          final provider = Map<String, dynamic>.from(e);
          provider['is_verified'] = verifiedIds.contains(provider['provider_id']);
          return provider;
        }).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _allProviders = [];
        _isLoading = false;
      });
    }
  }

  List<Map<String, dynamic>> get _filteredProviders {
    return _allProviders.where((provider) {
      // 1. Filter by Service Chip
      bool matchesChip = true;
      if (_selectedFilter != 'All') {
        final filterValue =
            filters.firstWhere((f) => f['label'] == _selectedFilter)['value'];
        List<dynamic> serviceTypes = provider['service_types'] ?? [];
        matchesChip = serviceTypes.contains(filterValue);
      }

      // 2. Filter by Search Query
      bool matchesSearch = true;
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        final name = provider['name'].toString().toLowerCase();
        List<dynamic> serviceTypes = provider['service_types'] ?? [];
        bool matchesServiceType =
            serviceTypes.any((s) => s.toString().toLowerCase().contains(query));
        matchesSearch = name.contains(query) || matchesServiceType;
      }

      return matchesChip && matchesSearch;
    }).toList();
  }

  Color _getServiceColor(String serviceType) {
    if (serviceType.contains('ac')) return const Color(0xFFFF6B35);
    if (serviceType.contains('plumb')) return const Color(0xFF1565C0);
    if (serviceType.contains('cook')) return const Color(0xFF2E7D32);
    if (serviceType.contains('beauti')) return const Color(0xFFAD1457);
    if (serviceType.contains('carpen')) return const Color(0xFF4E342E);
    if (serviceType.contains('elect')) return const Color(0xFFF9A825);
    if (serviceType.contains('paint')) return const Color(0xFF6A1B9A);
    if (serviceType.contains('mech')) return const Color(0xFF00695C);
    return const Color(0xFF1565C0);
  }

  @override
  Widget build(BuildContext context) {
    final displayProviders = _filteredProviders;

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
          widget.serviceType != null
              ? '${widget.serviceType} Providers'
              : 'Available Providers',
          style: GoogleFonts.poppins(
              color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Location/Budget info bar — API se aaya ho toh dikhao
          if (widget.location != null)
            Container(
              color: const Color(0xFFF0F4FF),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.location_on, color: Color(0xFF1565C0), size: 16),
                  const SizedBox(width: 4),
                  Text(
                    widget.location!,
                    style: GoogleFonts.poppins(
                        fontSize: 13, color: const Color(0xFF1565C0)),
                  ),
                  if (widget.budget != null) ...[
                    const SizedBox(width: 16),
                    const Icon(Icons.wallet, color: Color(0xFF2E7D32), size: 16),
                    const SizedBox(width: 4),
                    Text(
                      'Rs. ${widget.budget!.toInt()}',
                      style: GoogleFonts.poppins(
                          fontSize: 13, color: const Color(0xFF2E7D32)),
                    ),
                  ],
                ],
              ),
            ),

          // Female Safety Mode Toggle
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Text('👩', style: TextStyle(fontSize: 20)),
                    const SizedBox(width: 8),
                    Text(
                      'Female Safety Mode',
                      style: GoogleFonts.poppins(
                          fontWeight: FontWeight.bold,
                          color: Colors.pink,
                          fontSize: 15),
                    ),
                  ],
                ),
                Switch(
                  value: _femaleSafetyMode,
                  onChanged: (val) {
                    setState(() {
                      _femaleSafetyMode = val;
                    });
                  },
                  activeColor: Colors.pink,
                ),
              ],
            ),
          ),

          // Search Bar
          Container(
            color: Colors.white,
            padding: const EdgeInsets.fromLTRB(20, 10, 20, 10),
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFFF8F9FD),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.grey[200]!),
              ),
              child: TextField(
                onChanged: (value) {
                  setState(() {
                    _searchQuery = value;
                  });
                },
                style: GoogleFonts.poppins(),
                decoration: InputDecoration(
                  hintText: 'Search provider or service...',
                  hintStyle: GoogleFonts.poppins(color: Colors.grey),
                  prefixIcon:
                      const Icon(Icons.search, color: Color(0xFFFF6B35)),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
          ),

          // Filter Chips
          Container(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
            color: Colors.white,
            width: double.infinity,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: filters.map((filter) {
                  final label = filter['label']!;
                  final isSelected = _selectedFilter == label;
                  return Padding(
                    padding: const EdgeInsets.only(right: 12.0),
                    child: ChoiceChip(
                      label: Text(
                        label,
                        style: GoogleFonts.poppins(
                          color: isSelected ? Colors.white : Colors.black87,
                          fontWeight: isSelected
                              ? FontWeight.bold
                              : FontWeight.w500,
                        ),
                      ),
                      selected: isSelected,
                      onSelected: (selected) {
                        setState(() {
                          _selectedFilter = label;
                        });
                      },
                      selectedColor: const Color(0xFFFF6B35),
                      backgroundColor: Colors.white,
                      showCheckmark: false,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                        side: BorderSide(
                          color: isSelected
                              ? const Color(0xFFFF6B35)
                              : Colors.grey[300]!,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),

          // Showing Count
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 4),
            child: Text(
              'Showing ${displayProviders.length} providers',
              style: GoogleFonts.poppins(
                color: Colors.black54,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),

          // Provider List
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(
                        color: Color(0xFF1565C0)))
                : displayProviders.isEmpty
                    ? Center(
                        child: Text(
                          'No providers found matching your criteria.',
                          style: GoogleFonts.poppins(color: Colors.grey),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(20.0),
                        itemCount: displayProviders.length,
                        itemBuilder: (context, index) {
                          final provider = displayProviders[index];
                          final serviceTypes =
                              (provider['service_types'] as List? ?? [])
                                  .join(', ');
                          final aiScore =
                              ((provider['rating'] as num? ?? 0) * 20).toInt();
                          final Color serviceColor =
                              _getServiceColor(serviceTypes);
                          final bool isVerified =
                              provider['is_verified'] ?? false;
                          final bool isLocked =
                              _femaleSafetyMode && !isVerified;

                          return Opacity(
                            opacity: isLocked ? 0.6 : 1.0,
                            child: Container(
                              margin: const EdgeInsets.only(bottom: 16),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(16),
                                border: Border(
                                  left: BorderSide(
                                      color: serviceColor, width: 4),
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.06),
                                    blurRadius: 8,
                                    offset: const Offset(0, 4),
                                  ),
                                ],
                              ),
                              child: Stack(
                                children: [
                                  Padding(
                                    padding: const EdgeInsets.all(16.0),
                                    child: Row(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        // Avatar
                                        Container(
                                          width: 60,
                                          height: 60,
                                          decoration: BoxDecoration(
                                            color: serviceColor.withOpacity(0.1),
                                            shape: BoxShape.circle,
                                          ),
                                          child: Center(
                                            child: Text(
                                              _getInitials(
                                                  provider['name'] ?? '?'),
                                              style: GoogleFonts.poppins(
                                                color: serviceColor,
                                                fontWeight: FontWeight.bold,
                                                fontSize: 20,
                                              ),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 16),
                                        // Details
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                provider['name'] ?? 'Unknown',
                                                style: GoogleFonts.poppins(
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 16,
                                                  color: Colors.black87,
                                                ),
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                              const SizedBox(height: 4),
                                              if (isVerified)
                                                const VerifiedBadge()
                                              else
                                                Container(
                                                  padding: const EdgeInsets
                                                      .symmetric(
                                                      horizontal: 8,
                                                      vertical: 4),
                                                  decoration: BoxDecoration(
                                                    color: Colors.grey[200],
                                                    borderRadius:
                                                        BorderRadius.circular(
                                                            12),
                                                  ),
                                                  child: Text(
                                                    'Unverified',
                                                    style: GoogleFonts.poppins(
                                                      color: Colors.grey[600],
                                                      fontSize: 10,
                                                      fontWeight:
                                                          FontWeight.bold,
                                                    ),
                                                  ),
                                                ),
                                              const SizedBox(height: 8),
                                              Text(
                                                _capitalize(serviceTypes),
                                                style: GoogleFonts.poppins(
                                                  color: Colors.grey[600],
                                                  fontSize: 13,
                                                  fontWeight: FontWeight.w500,
                                                ),
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                              const SizedBox(height: 8),
                                              Row(
                                                children: [
                                                  const Icon(Icons.star,
                                                      color: Colors.amber,
                                                      size: 16),
                                                  Text(
                                                    ' ${provider['rating'] ?? 'N/A'}',
                                                    style: GoogleFonts.poppins(
                                                        fontWeight:
                                                            FontWeight.bold,
                                                        fontSize: 13),
                                                  ),
                                                  const SizedBox(width: 12),
                                                  const Icon(Icons.location_on,
                                                      color: Colors.grey,
                                                      size: 14),
                                                  Text(
                                                    ' ${provider['distance_km'] ?? 'N/A'} km',
                                                    style: GoogleFonts.poppins(
                                                        color: Colors.grey[600],
                                                        fontSize: 13),
                                                  ),
                                                ],
                                              ),
                                              const SizedBox(height: 16),
                                              Row(
                                                mainAxisAlignment:
                                                    MainAxisAlignment
                                                        .spaceBetween,
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.end,
                                                children: [
                                                  Text(
                                                    'Rs.${provider['base_rate_pkr'] ?? 'N/A'}',
                                                    style: GoogleFonts.poppins(
                                                      color: Colors.green,
                                                      fontWeight:
                                                          FontWeight.bold,
                                                      fontSize: 16,
                                                    ),
                                                  ),
                                                  Container(
                                                    decoration: BoxDecoration(
                                                      gradient: isLocked
                                                          ? LinearGradient(
                                                              colors: [
                                                                Colors
                                                                    .grey[400]!,
                                                                Colors.grey[500]!
                                                              ],
                                                            )
                                                          : const LinearGradient(
                                                              colors: [
                                                                Color(
                                                                    0xFFFF6B35),
                                                                Color(
                                                                    0xFFFF8C42),
                                                              ],
                                                            ),
                                                      borderRadius:
                                                          BorderRadius.circular(
                                                              10),
                                                      boxShadow: isLocked
                                                          ? null
                                                          : [
                                                              BoxShadow(
                                                                color: const Color(
                                                                        0xFFFF6B35)
                                                                    .withOpacity(
                                                                        0.3),
                                                                blurRadius: 8,
                                                                offset:
                                                                    const Offset(
                                                                        0, 3),
                                                              ),
                                                            ],
                                                    ),
                                                    child: ElevatedButton(
                                                      onPressed: () {
                                                        if (_femaleSafetyMode) {
                                                          if (isVerified) {
                                                            Navigator.push(
                                                              context,
                                                              MaterialPageRoute(
                                                                builder: (context) =>
                                                                    FemaleSafetyBookingScreen(
                                                                        provider:
                                                                            provider),
                                                              ),
                                                            );
                                                          } else {
                                                            showDialog(
                                                              context: context,
                                                              builder: (context) =>
                                                                  AlertDialog(
                                                                shape: RoundedRectangleBorder(
                                                                    borderRadius:
                                                                        BorderRadius.circular(
                                                                            16)),
                                                                title: Row(
                                                                  children: [
                                                                    const Icon(
                                                                        Icons
                                                                            .warning_amber_rounded,
                                                                        color: Colors
                                                                            .redAccent,
                                                                        size:
                                                                            28),
                                                                    const SizedBox(
                                                                        width:
                                                                            8),
                                                                    Text(
                                                                        'Safety Alert',
                                                                        style: GoogleFonts.poppins(
                                                                            fontWeight: FontWeight
                                                                                .bold,
                                                                            color: const Color(
                                                                                0xFF0A2463))),
                                                                  ],
                                                                ),
                                                                content: Text(
                                                                    'This provider is not verified. For your safety, please choose a verified provider.',
                                                                    style: GoogleFonts
                                                                        .poppins()),
                                                                actions: [
                                                                  TextButton(
                                                                    onPressed: () =>
                                                                        Navigator.pop(
                                                                            context),
                                                                    child: Text(
                                                                        'OK',
                                                                        style: GoogleFonts.poppins(
                                                                            color: const Color(
                                                                                0xFF1565C0),
                                                                            fontWeight:
                                                                                FontWeight.bold)),
                                                                  ),
                                                                ],
                                                              ),
                                                            );
                                                          }
                                                        } else {
                                                          Navigator.push(
                                                            context,
                                                            MaterialPageRoute(
                                                              builder: (context) =>
                                                                  BookingConfirmScreen(
                                                                provider:
                                                                    provider,
                                                                femaleSafetyMode:
                                                                    _femaleSafetyMode,
                                                              ),
                                                            ),
                                                          );
                                                        }
                                                      },
                                                      style: ElevatedButton
                                                          .styleFrom(
                                                        backgroundColor:
                                                            Colors.transparent,
                                                        shadowColor:
                                                            Colors.transparent,
                                                        disabledBackgroundColor:
                                                            Colors.transparent,
                                                        shape:
                                                            RoundedRectangleBorder(
                                                          borderRadius:
                                                              BorderRadius
                                                                  .circular(10),
                                                        ),
                                                        padding:
                                                            const EdgeInsets
                                                                .symmetric(
                                                                horizontal: 24,
                                                                vertical: 8),
                                                      ),
                                                      child: Row(
                                                        mainAxisSize:
                                                            MainAxisSize.min,
                                                        children: [
                                                          if (isLocked)
                                                            const Icon(
                                                                Icons.lock,
                                                                size: 14,
                                                                color: Colors
                                                                    .white),
                                                          if (isLocked)
                                                            const SizedBox(
                                                                width: 4),
                                                          Text('Book Now',
                                                              style: GoogleFonts
                                                                  .poppins(
                                                                      fontWeight:
                                                                          FontWeight
                                                                              .bold,
                                                                      color: Colors
                                                                          .white)),
                                                        ],
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
                                  ),
                                  // AI Score Badge
                                  Positioned(
                                    top: 16,
                                    right: 16,
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(
                                          horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFFFFF3E0),
                                        borderRadius:
                                            BorderRadius.circular(20),
                                        border: Border.all(
                                            color: const Color(0xFFFFCC80)),
                                      ),
                                      child: Text(
                                        'AI Score: $aiScore%',
                                        style: GoogleFonts.poppins(
                                          color: const Color(0xFFE65100),
                                          fontSize: 10,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
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

  String _getInitials(String name) {
    List<String> names = name.split(" ");
    String initials = "";
    int numWords = names.length > 2 ? 2 : names.length;
    for (int i = 0; i < numWords; i++) {
      if (names[i].isNotEmpty) {
        initials += names[i][0];
      }
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