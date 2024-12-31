  export interface Profile {
    job_title: string;
    location: string;
    photo_url: string;
    linkedin_url: string;
  }
  
  export interface Party {
    name: string;
    email?: string;
    profile?: Profile;
  }
  
  export interface CallMetadata {
    call_id: string
    title: string;
    duration: number;
    start_time: string;
    parties: Party[];
  }
  
  export interface Message {
    content: string;
    role: string;
  }
