export interface ApiChannel {
  id: string;
  name: string;
  status: "live" | "dead" | "unknown";
}

export interface ApiStream {
  id: string;
  url: string;
  subtype: "hls" | "embed";
}

export interface ApiEvent {
  id: string;
  type: string;
  status: "SCHEDULED" | "LIVE" | "FINISHED";
  title: string;
  sport: string | null;
  competition: string | null;
  home_team: string | null;
  away_team: string | null;
  start_time: string | null;
  external_id: string | null;
  poster_url: string | null;
}
