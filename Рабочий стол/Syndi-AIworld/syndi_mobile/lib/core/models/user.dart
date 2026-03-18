class UserProfile {
  final int id;
  final String name;
  final String? email;
  final BigFiveProfile? bigFive;
  final DateTime createdAt;

  UserProfile({
    required this.id,
    required this.name,
    this.email,
    this.bigFive,
    required this.createdAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      bigFive: json['big_five'] != null 
          ? BigFiveProfile.fromJson(json['big_five'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'big_five': bigFive?.toJson(),
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class BigFiveProfile {
  final double openness;
  final double conscientiousness;
  final double extraversion;
  final double agreeableness;
  final double neuroticism;

  BigFiveProfile({
    required this.openness,
    required this.conscientiousness,
    required this.extraversion,
    required this.agreeableness,
    required this.neuroticism,
  });

  factory BigFiveProfile.fromJson(Map<String, dynamic> json) {
    return BigFiveProfile(
      openness: json['openness'].toDouble(),
      conscientiousness: json['conscientiousness'].toDouble(),
      extraversion: json['extraversion'].toDouble(),
      agreeableness: json['agreeableness'].toDouble(),
      neuroticism: json['neuroticism'].toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'openness': openness,
      'conscientiousness': conscientiousness,
      'extraversion': extraversion,
      'agreeableness': agreeableness,
      'neuroticism': neuroticism,
    };
  }

  String getPersonalityType() {
    if (openness > 0.7) return 'Творец';
    if (conscientiousness > 0.7) return 'Организатор';
    if (extraversion > 0.7) return 'Душа компании';
    if (agreeableness > 0.7) return 'Дипломат';
    if (neuroticism > 0.7) return 'Чувствительный';
    return 'Сбалансированный';
  }
}

class Match {
  final UserProfile user;
  final double compatibility;
  final String reason;

  Match({
    required this.user,
    required this.compatibility,
    required this.reason,
  });

  factory Match.fromJson(Map<String, dynamic> json) {
    return Match(
      user: UserProfile.fromJson(json['user']),
      compatibility: json['compatibility'].toDouble(),
      reason: json['reason'],
    );
  }
}
