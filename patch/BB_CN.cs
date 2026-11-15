using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

public static class BB_CN
{
	private const int CacheLimit = 20000;

	private static Dictionary<string, string> exact;
	private static List<Template> templates;
	private static Dictionary<string, string> cache = new Dictionary<string, string>();
	private static Dictionary<int, KeyValuePair<string, string>> shown = new Dictionary<int, KeyValuePair<string, string>>();
	private static HashSet<string> dumped;
	private static string dumpPath;

	private sealed class Template
	{
		public string[] Parts;
		public string[] Output;
		public int[] Slots;
	}

	// Characters that may not begin a line, and characters that may not end one.
	private const string NoLineStart = "，。！？；：、）】》」』’”…—·%％,.!?;:)]";
	private const string NoLineEnd = "（【《「『‘“([";

	private static void Load()
	{
		exact = new Dictionary<string, string>();
		templates = new List<Template>();
		string dir = Path.Combine(Application.dataPath, "BB_CN");
		string[] files = Directory.Exists(dir) ? Directory.GetFiles(dir, "*.tsv") : new string[0];
		Array.Sort(files, StringComparer.Ordinal);
		foreach (string file in files)
		{
			foreach (string line in File.ReadAllLines(file, Encoding.UTF8))
			{
				if (line.Length == 0 || line[0] == '#')
				{
					continue;
				}
				int tab = line.IndexOf('\t');
				if (tab <= 0 || tab == line.Length - 1)
				{
					continue;
				}
				string en = Unescape(line.Substring(0, tab));
				string zh = Unescape(line.Substring(tab + 1));
				if (en.IndexOf("{0}", StringComparison.Ordinal) >= 0)
				{
					templates.Add(MakeTemplate(en, zh));
				}
				else
				{
					exact[en] = zh;
				}
			}
		}
		if (File.Exists(Path.Combine(dir, "dump.on")))
		{
			dumpPath = Path.Combine(dir, "misses.txt");
			dumped = new HashSet<string>();
			if (File.Exists(dumpPath))
			{
				foreach (string line in File.ReadAllLines(dumpPath, Encoding.UTF8))
				{
					dumped.Add(line);
				}
			}
		}
	}

	private static string Unescape(string s)
	{
		return s.Replace("\\r", "\r").Replace("\\n", "\n").Replace("\\t", "\t");
	}

	private static Template MakeTemplate(string en, string zh)
	{
		List<string> parts = new List<string>();
		List<int> slots = new List<int>();
		int pos = 0;
		while (true)
		{
			int open = en.IndexOf('{', pos);
			if (open < 0 || open + 2 >= en.Length || en[open + 2] != '}' || !char.IsDigit(en[open + 1]))
			{
				break;
			}
			parts.Add(en.Substring(pos, open - pos));
			slots.Add(en[open + 1] - '0');
			pos = open + 3;
		}
		parts.Add(en.Substring(pos));
		Template t = new Template();
		t.Parts = parts.ToArray();
		t.Slots = slots.ToArray();
		t.Output = new string[] { zh };
		return t;
	}

	private static bool Match(Template t, string s, out string result)
	{
		result = null;
		string[] parts = t.Parts;
		// A single-line template must not swallow a multi-line block. "Level {0}" would
		// otherwise claim every location readout and leave the real multi-line template unused.
		bool templateHasNewline = false;
		for (int p = 0; p < parts.Length; p++)
		{
			if (parts[p].IndexOf('\n') >= 0)
			{
				templateHasNewline = true;
				break;
			}
		}
		if (!templateHasNewline && s.IndexOf('\n') >= 0)
		{
			return false;
		}
		if (!s.StartsWith(parts[0], StringComparison.Ordinal) || !s.EndsWith(parts[parts.Length - 1], StringComparison.Ordinal))
		{
			return false;
		}
		string[] values = new string[10];
		int pos = parts[0].Length;
		int end = s.Length - parts[parts.Length - 1].Length;
		if (end < pos)
		{
			return false;
		}
		for (int i = 0; i < t.Slots.Length; i++)
		{
			int next;
			if (i == t.Slots.Length - 1)
			{
				next = end;
			}
			else
			{
				// An empty separator, or a search that starts at the end of the string, makes
				// IndexOf throw (count == 0) and kills the caller. Treat that as "no match".
				int searchFrom = pos + 1;
				if (searchFrom >= s.Length || parts[i + 1].Length == 0)
				{
					return false;
				}
				next = s.IndexOf(parts[i + 1], searchFrom, StringComparison.Ordinal);
				if (next < 0 || next > end)
				{
					return false;
				}
			}
			if (next <= pos || next > s.Length)
			{
				return false;
			}
			// "Man{0}" must not eat the word Manpower. A slot boundary inside a word is not a match.
			if (pos > 0 && pos < s.Length && char.IsLetter(s[pos - 1]) && char.IsLetter(s[pos]))
			{
				return false;
			}
			if (next > 0 && next < s.Length && char.IsLetter(s[next - 1]) && char.IsLetter(s[next]))
			{
				return false;
			}
			// An empty ending on a single-line template must not swallow the following lines.
			// A template that already contains a newline, such as "LOADING\n\n{0}", is meant to.
			if (i == t.Slots.Length - 1 && parts[parts.Length - 1].Length == 0 && !templateHasNewline && s.IndexOf('\n', pos, next - pos) >= 0)
			{
				return false;
			}
			// "Manpower 38722" is a number. "Manpower is important!" is a sentence.
			if (i == t.Slots.Length - 1 && (parts[0] == "Manpower " || parts[0] == "Supports " || parts[0] == "Upkeep " || parts[0] == "Level "))
			{
				for (int c = pos; c < next; c++)
				{
					if (char.IsLetter(s[c]))
					{
						return false;
					}
				}
			}
			// "Name, the Murderer" is a title. "Yeah, the door is open." is a sentence.
			if (parts[i].EndsWith(", the ", StringComparison.Ordinal) && (next - pos > 40 || s.IndexOf('.', pos, next - pos) >= 0 || s.IndexOf('\n', pos, next - pos) >= 0))
			{
				return false;
			}
			// "Band of 28" is a count. The save card continues with a location on the next line,
			// and "{0}\nBand of {1}" must not glue 人团伙 onto that location.
			if (parts[i].EndsWith("Band of ", StringComparison.Ordinal))
			{
				for (int c = pos; c < next; c++)
				{
					char ch = s[c];
					if (ch == '\n' || (ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z'))
					{
						return false;
					}
				}
			}
			values[t.Slots[i]] = Translate(s.Substring(pos, next - pos));
			pos = next + parts[i + 1].Length;
		}
		string output = t.Output[0];
		for (int i = 0; i < 10; i++)
		{
			if (values[i] != null)
			{
				output = output.Replace("{" + i + "}", values[i]);
			}
		}
		result = output;
		return true;
	}

	private static bool HasLetters(string s)
	{
		// A Chinese name filled into an English sentence still has to be matched.
		// Only a string with no ASCII letters is already display text.
		for (int i = 0; i < s.Length; i++)
		{
			char c = s[i];
			if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z'))
			{
				return true;
			}
		}
		return false;
	}

	public static string T(string s)
	{
		if (s == null || s.Length == 0 || !HasLetters(s))
		{
			return s;
		}
		if (exact == null)
		{
			Load();
		}
		string result;
		if (cache.TryGetValue(s, out result))
		{
			return result;
		}
		try
		{
			result = Translate(s);
		}
		catch (Exception)
		{
			result = s;
		}
		if (cache.Count >= CacheLimit)
		{
			cache.Clear();
		}
		cache[s] = result;
		return result;
	}

	// Crime names are inserted with ToLower(), and "a murderer" / "an apostate" wrap the nickname.
	private static bool TryFolded(string s, out string result)
	{
		result = null;
		string key = null;
		if (s.StartsWith("an ", StringComparison.Ordinal) && s.Length > 4)
		{
			key = char.ToUpper(s[3]) + s.Substring(4);
		}
		else if (s.StartsWith("a ", StringComparison.Ordinal) && s.Length > 3)
		{
			key = char.ToUpper(s[2]) + s.Substring(3);
		}
		else if (s.Length > 1 && s[0] >= 'a' && s[0] <= 'z' && s.IndexOf(' ') < 0)
		{
			key = char.ToUpper(s[0]) + s.Substring(1);
		}
		return key != null && exact.TryGetValue(key, out result);
	}

	private static string Translate(string s)
	{
		// Slot values call Translate directly. A Chinese name has nothing to look up,
		// and a template that starts with {0} must not swallow it.
		if (s == null || s.Length == 0 || !HasLetters(s))
		{
			return s;
		}
		string result;
		if (exact.TryGetValue(s, out result) || TryFolded(s, out result))
		{
			return result;
		}
		// Dialogue files wrap a stored line in quotes. Only peel them when the
		// inside is an exact entry. Recursive matching here lets a short template
		// such as "{0}, the {1}" eat "Defendant, the court has deliberated...".
		if (s.Length >= 2 && s[0] == '"' && s[s.Length - 1] == '"')
		{
			string inner = s.Substring(1, s.Length - 2);
			string spoken;
			if (inner.Length > 0 && exact.TryGetValue(inner, out spoken))
			{
				return "“" + spoken + "”";
			}
		}
		int start = 0;
		int end = s.Length;
		while (start < end && char.IsWhiteSpace(s[start]))
		{
			start++;
		}
		while (end > start && char.IsWhiteSpace(s[end - 1]))
		{
			end--;
		}
		if (start > 0 || end < s.Length)
		{
			string core = s.Substring(start, end - start);
			if (core.Length > 0 && HasLetters(core))
			{
				string inner = Translate(core);
				if (!ReferenceEquals(inner, core))
				{
					return s.Substring(0, start) + inner + s.Substring(end);
				}
			}
			return s;
		}
		// Floating barks are "Name: line". Match this before templates, or a short
		// pattern such as "{0} in {1}" eats the sentence and leaves the tail in English.
		int colon = s.IndexOf(": ", StringComparison.Ordinal);
		if (colon > 0 && colon <= 32)
		{
			string spoken;
			if (exact.TryGetValue(s.Substring(colon + 2), out spoken))
			{
				return s.Substring(0, colon) + "：" + spoken;
			}
		}
		for (int i = 0; i < templates.Count; i++)
		{
			if (Match(templates[i], s, out result))
			{
				return result;
			}
		}
		// Party plates are "Name - Crime" or "Name - Alleged Crime".
		int dash = s.IndexOf(" - ", StringComparison.Ordinal);
		if (dash > 0 && dash <= 32 && s.IndexOf(" - ", dash + 3, StringComparison.Ordinal) < 0)
		{
			string right = s.Substring(dash + 3);
			string rightZh = Translate(right);
			if (!ReferenceEquals(rightZh, right))
			{
				return s.Substring(0, dash) + " - " + rightZh;
			}
		}
		if (s.IndexOf('\n') >= 0)
		{
			string[] lines = s.Split('\n');
			bool changed = false;
			for (int i = 0; i < lines.Length; i++)
			{
				string line = Translate(lines[i]);
				changed |= !ReferenceEquals(line, lines[i]);
				lines[i] = line;
			}
			if (changed)
			{
				return string.Join("\n", lines);
			}
			return s;
		}
		Miss(s);
		return s;
	}

	private static void Miss(string s)
	{
		if (dumped == null)
		{
			return;
		}
		string line = s.Replace("\n", "\\n").Replace("\t", "\\t");
		if (dumped.Add(line))
		{
			try
			{
				File.AppendAllText(dumpPath, line + "\n", Encoding.UTF8);
			}
			catch
			{
			}
		}
	}

	public static void SetText(TextMesh tm, string s)
	{
		string zh = T(s);
		tm.text = zh;
		Remember(tm, s, zh);
	}

	public static string GetText(TextMesh tm)
	{
		string current = tm.text;
		KeyValuePair<string, string> pair;
		if (shown.TryGetValue(tm.GetInstanceID(), out pair) && pair.Value == current)
		{
			return pair.Key;
		}
		return current;
	}

	private static void Remember(TextMesh tm, string en, string zh)
	{
		int id = tm.GetInstanceID();
		if (ReferenceEquals(en, zh) || en == zh)
		{
			shown.Remove(id);
			return;
		}
		if (shown.Count >= CacheLimit)
		{
			shown.Clear();
		}
		shown[id] = new KeyValuePair<string, string>(en, zh);
	}

	private static bool IsCjk(char c)
	{
		return c >= 0x2E80 || (c >= 0x2000 && (NoLineStart.IndexOf(c) >= 0 || NoLineEnd.IndexOf(c) >= 0));
	}

	// Line-break units: a Latin word (with its leading spaces) or one CJK character.
	// Opening brackets stick to the following unit and closing punctuation to the preceding one.
	private static List<string> Tokens(string paragraph)
	{
		List<string> tokens = new List<string>();
		StringBuilder cur = new StringBuilder();
		bool curHasText = false;
		bool curOpenOnly = false;
		for (int i = 0; i < paragraph.Length; i++)
		{
			char c = paragraph[i];
			bool breakable = curHasText && !curOpenOnly;
			if (c == ' ')
			{
				if (breakable)
				{
					tokens.Add(cur.ToString());
					cur.Length = 0;
					curHasText = false;
				}
				cur.Append(c);
				continue;
			}
			if (NoLineStart.IndexOf(c) >= 0)
			{
				if (!curHasText && tokens.Count > 0)
				{
					tokens[tokens.Count - 1] += cur.ToString() + c;
					cur.Length = 0;
				}
				else
				{
					cur.Append(c);
					curHasText = true;
				}
				continue;
			}
			bool open = NoLineEnd.IndexOf(c) >= 0;
			bool cjk = IsCjk(c);
			if ((open || cjk) && breakable)
			{
				tokens.Add(cur.ToString());
				cur.Length = 0;
				curHasText = false;
			}
			if (!curHasText)
			{
				curOpenOnly = true;
			}
			cur.Append(c);
			curHasText = true;
			curOpenOnly &= open;
			if (cjk && !open)
			{
				tokens.Add(cur.ToString());
				cur.Length = 0;
				curHasText = false;
			}
		}
		if (cur.Length > 0)
		{
			tokens.Add(cur.ToString());
		}
		return tokens;
	}

	private static float Width(TextMesh tm, string s)
	{
		tm.text = s;
		Bounds b = tm.renderer.bounds;
		return b.max.x - b.min.x;
	}

	public static string Wrap(TextMesh tm, string text, int width)
	{
		StringBuilder output = new StringBuilder();
		string[] paragraphs = text.Split('\n');
		for (int p = 0; p < paragraphs.Length; p++)
		{
			if (p > 0)
			{
				output.Append('\n');
			}
			string line = string.Empty;
			foreach (string token in Tokens(paragraphs[p]))
			{
				string candidate = line + token;
				if (line.Length > 0 && Width(tm, candidate) > width)
				{
					output.Append(line.TrimEnd(' ')).Append('\n');
					line = token.TrimStart(' ');
				}
				else
				{
					line = candidate;
				}
			}
			output.Append(line);
		}
		return output.ToString();
	}

	public static TextMesh MakeLabel(PixelGUI gui, string name, Vector3 coord, string txt, int size, int width, bool frame, TextAnchor orientation)
	{
		GameObject gameObject = (GameObject)UnityEngine.Object.Instantiate(gui.textField, coord, Quaternion.identity);
		gameObject.name = name;
		gameObject.transform.localScale = gameObject.transform.localScale * size;
		TextMesh component = gameObject.GetComponent<TextMesh>();
		string en = txt;
		txt = T(txt);
		if (frame)
		{
			txt = Wrap(component, txt, width);
			Align(component, width, orientation);
		}
		component.text = txt;
		Remember(component, en, txt);
		component.anchor = orientation;
		return component;
	}

	public static TextMesh MakeScrollLabel(PixelGUI gui, string gameObjectName, Vector3 coord, string txt, int size, int width, bool frame, TextAnchor orientation, TextAlignment alignment)
	{
		GameObject gameObject = (GameObject)UnityEngine.Object.Instantiate(gui.textField, coord, Quaternion.identity);
		gameObject.name = gui.name;
		gameObject.transform.localScale = gameObject.transform.localScale * size;
		TextMesh component = gameObject.GetComponent<TextMesh>();
		txt = T(txt);
		if (frame)
		{
			txt = Wrap(component, txt, width);
			Align(component, width, orientation);
		}
		component.text = txt;
		component.anchor = orientation;
		return component;
	}

	private static void Align(TextMesh component, int width, TextAnchor orientation)
	{
		switch (orientation)
		{
		default:
			component.alignment = TextAlignment.Left;
			break;
		case TextAnchor.UpperCenter:
			component.transform.position = component.transform.position + new Vector3(width / 2, 0f, 0f);
			component.alignment = TextAlignment.Center;
			break;
		case TextAnchor.UpperRight:
			component.transform.position = component.transform.position + new Vector3(width, 0f, 0f);
			component.alignment = TextAlignment.Right;
			break;
		}
	}

	public static GameObject MakeGUIMessagePanel(PixelGUI gui, Camera cam, Vector2 coord, string title, string label)
	{
		int num = 64;
		int num2 = 32;
		GameObject gameObject = (GameObject)UnityEngine.Object.Instantiate(gui.GUIMessage, cam.transform.position + -new Vector3(Screen.width / 2, Screen.height / 2, 0f) + new Vector3(Mathf.Clamp(coord.x, num, Screen.width - num), Mathf.Clamp(coord.y, num2, Screen.height - num2), 0.6f), Quaternion.identity);
		gameObject.name = "GUIMessagePanel";
		TextMesh[] texts = gameObject.GetComponentsInChildren<TextMesh>();
		SetText(texts[1], title);
		string text = Wrap(texts[0], T(label), 475);
		texts[0].text = text;
		Remember(texts[0], label, text);
		int lines = text.Split('\n').Length;
		texts[0].transform.position = texts[0].transform.position + new Vector3(0f, (5 - lines) * 10, 0f);
		gameObject.transform.parent = cam.transform;
		return gameObject;
	}
}
