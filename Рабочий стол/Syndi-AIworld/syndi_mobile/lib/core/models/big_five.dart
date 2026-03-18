class BigFiveQuestion {
  final int id;
  final String text;
  final String trait;
  final bool isReversed;

  BigFiveQuestion({
    required this.id,
    required this.text,
    required this.trait,
    required this.isReversed,
  });

  factory BigFiveQuestion.fromJson(Map<String, dynamic> json) {
    return BigFiveQuestion(
      id: json['id'],
      text: json['text'],
      trait: json['trait'],
      isReversed: json['is_reversed'] ?? false,
    );
  }
}

class BigFiveAnswer {
  final int questionId;
  final int score; // 1-5

  BigFiveAnswer({
    required this.questionId,
    required this.score,
  });

  Map<String, dynamic> toJson() {
    return {
      'question_id': questionId,
      'score': score,
    };
  }
}
