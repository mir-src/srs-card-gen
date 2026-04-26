using System;

namespace Exporter;

public class Flashcard
{
    public string? front { get; set; }
    public string? back { get; set; }
    public string? audio_front { get; set; }
    public string? audio_back { get; set; }
    public string? cloze_text { get; set; }
    public string? card_type { get; set; }
}
