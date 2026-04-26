export interface OceanScores {
  openness:          number; // 0-100
  conscientiousness: number;
  extraversion:      number;
  agreeableness:     number;
  neuroticism:       number;
}

export interface UserProfile {
  id:                 string;
  name:               string;
  email:              string;
  role:               string;
  bio?:               string;
  skills?:            string[];
  location?:          string;
  avatar_url?:        string;
  ocean_openness?:          number;
  ocean_conscientiousness?: number;
  ocean_extraversion?:      number;
  ocean_agreeableness?:     number;
  ocean_neuroticism?:       number;
}

export interface MatchResult {
  user:              UserProfile;
  score:             number;        // 0-100
  compatibility:     OceanScores;   // разбивка по трейтам
}

export interface Match {
  id:             string;
  matched_user:   UserProfile;
  score:          number;
  created_at:     string;
}
