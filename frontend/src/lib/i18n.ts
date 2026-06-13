// Local fallback for UI strings; the app prefers /api/ui-strings on load.
export type UiStrings = {
  page_subtitle: string;
  chat_input_placeholder: string;
  voice_section_caption: string;
  voice_start: string;
  voice_stop: string;
  spinner_transcribing: string;
  spinner_switching: string;
  spinner_tts: string;
  warn_inaudible: string;
  err_transcription: string;
  err_response: string;
  sidebar_new_chat: string;
  greeting: string;
  topic_crops: string;
  topic_pests: string;
  topic_soil: string;
  topic_livestock: string;
  listening: string;
  understanding: string;
  offline: string;
  switch_to: string;
};

export const UI: Record<string, UiStrings> = {
  English: {
    page_subtitle: "Type or speak your farming question.",
    chat_input_placeholder: "Type your farming question…",
    voice_section_caption: "Press and hold to talk.",
    voice_start: "Hold to talk",
    voice_stop: "Release to send",
    spinner_transcribing: "Understanding…",
    spinner_switching: "Switching language…",
    spinner_tts: "Generating voice…",
    warn_inaudible: "Could not hear you. Please speak clearly and try again.",
    err_transcription: "Transcription failed",
    err_response: "Response error",
    sidebar_new_chat: "New conversation",
    greeting: "Good day, farmer.",
    topic_crops: "Crops",
    topic_pests: "Pests",
    topic_soil: "Soil",
    topic_livestock: "Livestock",
    listening: "Listening…",
    understanding: "Understanding…",
    offline: "You're offline. Messages will send when you reconnect.",
    switch_to: "Switch to",
  },
  Pidgin: {
    page_subtitle: "Type or talk your farm question.",
    chat_input_placeholder: "Type your farm question…",
    voice_section_caption: "Press and hold to talk.",
    voice_start: "Hold to talk",
    voice_stop: "Leave am to send",
    spinner_transcribing: "E dey hear you…",
    spinner_switching: "E dey change language…",
    spinner_tts: "E dey form voice…",
    warn_inaudible: "E no hear you well. Talk clear, try again.",
    err_transcription: "E no fit hear you",
    err_response: "Wahala with answer",
    sidebar_new_chat: "Start new talk",
    greeting: "How you dey, farmer.",
    topic_crops: "Crops",
    topic_pests: "Pests",
    topic_soil: "Soil",
    topic_livestock: "Animals",
    listening: "E dey hear you…",
    understanding: "E dey understand…",
    offline: "No network. E go send when you get connection.",
    switch_to: "Switch to",
  },
  Yoruba: {
    page_subtitle: "Tẹ tàbí sọ ìbéèrè oko rẹ.",
    chat_input_placeholder: "Tẹ ìbéèrè oko rẹ…",
    voice_section_caption: "Tẹ kí o sì dìmú láti sọ̀rọ̀.",
    voice_start: "Dìmú láti sọ̀rọ̀",
    voice_stop: "Tú sílẹ̀ láti firanṣẹ́",
    spinner_transcribing: "Ń gbọ́ ọ…",
    spinner_switching: "Ń yí èdè padà…",
    spinner_tts: "Ń ṣẹ̀dá ohùn…",
    warn_inaudible: "Kò gbọ́ ohun rẹ. Jọwọ́ sọ̀rọ̀ kedere.",
    err_transcription: "Ìtumọ̀ kùnà",
    err_response: "Àṣìṣe ìdáhùn",
    sidebar_new_chat: "Ìjọ̀sọ̀ tuntun",
    greeting: "Ẹ kú ọjọ́, àgbẹ̀.",
    topic_crops: "Irúgbìn",
    topic_pests: "Kòkòrò",
    topic_soil: "Ilẹ̀",
    topic_livestock: "Ẹran",
    listening: "Mo ń gbọ́…",
    understanding: "Ń gbọ́ ọ…",
    offline: "O kò sí lórí Íńtánẹ́ẹ̀tì.",
    switch_to: "Yí padà sí",
  },
  Igbo: {
    page_subtitle: "Pịnye ma ọ bụ kwuo ajụjụ ubi gị.",
    chat_input_placeholder: "Pịnye ajụjụ ubi gị…",
    voice_section_caption: "Pịa ma jide iji kwuo.",
    voice_start: "Jide iji kwuo",
    voice_stop: "Hapụ iji zipu",
    spinner_transcribing: "Ana m anụ gị…",
    spinner_switching: "Na-agbanwe asụsụ…",
    spinner_tts: "Na-emepụta olu…",
    warn_inaudible: "Anaghị m anụ gị. Biko kwuo nke ọma.",
    err_transcription: "Ntụgharị dara ada",
    err_response: "Njehie nzaghachi",
    sidebar_new_chat: "Mkparịta ụka ọhụrụ",
    greeting: "Ụbọchị ọma, onye ọrụ ubi.",
    topic_crops: "Ihe ọkụkụ",
    topic_pests: "Ụmụ ahụhụ",
    topic_soil: "Ala",
    topic_livestock: "Anụ ụlọ",
    listening: "Ana m ege ntị…",
    understanding: "Ana m anụ gị…",
    offline: "Ị nweghị Intanet.",
    switch_to: "Gbanwee gaa",
  },
  Hausa: {
    page_subtitle: "Rubuta ko faɗi tambayar noma ka.",
    chat_input_placeholder: "Rubuta tambayar noma ka…",
    voice_section_caption: "Danna ka riƙe don magana.",
    voice_start: "Riƙe don magana",
    voice_stop: "Saki don aikawa",
    spinner_transcribing: "Ina jin ka…",
    spinner_switching: "Ana canza harshe…",
    spinner_tts: "Ana samar da murya…",
    warn_inaudible: "Ban ji ka ba. Don Allah yi magana a fili.",
    err_transcription: "Rubutun magana ya kasa",
    err_response: "Kuskuren amsa",
    sidebar_new_chat: "Sabon tattaunawa",
    greeting: "Barka da rana, manomi.",
    topic_crops: "Amfanin gona",
    topic_pests: "Kwari",
    topic_soil: "Ƙasa",
    topic_livestock: "Dabbobi",
    listening: "Ina jin ka…",
    understanding: "Ina jin ka…",
    offline: "Babu Intanet.",
    switch_to: "Canja zuwa",
  },
};

export function ui(lang: string): UiStrings {
  return UI[lang] || UI.English;
}
