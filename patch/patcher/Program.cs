using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

// Usage: patcher <original Assembly-CSharp.dll> <BB_CN.dll> <literals.tsv> <output dll> [managed dir]
string sourcePath = args[0];
string helperPath = args[1];
string literalsPath = args[2];
string outputPath = args[3];

var resolver = new DefaultAssemblyResolver();
resolver.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(sourcePath)));
resolver.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(helperPath)));
resolver.AddSearchDirectory(Path.GetDirectoryName(Path.GetFullPath(outputPath)));
if (args.Length >= 5)
{
	resolver.AddSearchDirectory(Path.GetFullPath(args[4]));
}
var readerParams = new ReaderParameters { AssemblyResolver = resolver };

var assembly = AssemblyDefinition.ReadAssembly(sourcePath, readerParams);
var module = assembly.MainModule;
var helper = AssemblyDefinition.ReadAssembly(helperPath, readerParams).MainModule.GetType("BB_CN");
MethodReference Helper(string name) => module.ImportReference(helper.Methods.Single(m => m.Name == name && m.IsPublic));

// PixelGUI's word-wrapping label builders are delegated wholesale to BB_CN.
var pixelGui = module.GetType("PixelGUI");
var delegated = new HashSet<MethodDefinition>();
foreach (var name in new[] { "MakeLabel", "MakeScrollLabel", "MakeGUIMessagePanel" })
{
	var method = pixelGui.Methods.Single(m => m.Name == name);
	var target = Helper(name);
	if (target.Parameters.Count != method.Parameters.Count + 1)
	{
		throw new Exception($"{name}: helper signature mismatch");
	}
	method.Body.Instructions.Clear();
	method.Body.ExceptionHandlers.Clear();
	method.Body.Variables.Clear();
	var il = method.Body.GetILProcessor();
	il.Emit(OpCodes.Ldarg_0);
	foreach (var p in method.Parameters)
	{
		il.Emit(OpCodes.Ldarg, p);
	}
	il.Emit(OpCodes.Call, target);
	il.Emit(OpCodes.Ret);
	delegated.Add(method);
	Console.WriteLine("delegated PixelGUI." + name);
}

// Every other TextMesh.text access goes through the translation layer, except the
// typewriter coroutines, which re-set substrings of text that is already translated.
var setText = Helper("SetText");
var getText = Helper("GetText");
int sets = 0, gets = 0;
foreach (var type in module.GetTypes())
{
	foreach (var method in type.Methods.Where(m => m.HasBody && !delegated.Contains(m)))
	{
		bool typewriter = method.Name.Contains("ScrollText") || type.Name.Contains("ScrollText");
		if (typewriter)
		{
			Console.WriteLine("skipped " + type.FullName + "." + method.Name);
			continue;
		}
		foreach (var ins in method.Body.Instructions)
		{
			if ((ins.OpCode == OpCodes.Callvirt || ins.OpCode == OpCodes.Call) && ins.Operand is MethodReference mr &&
				mr.DeclaringType.FullName == "UnityEngine.TextMesh")
			{
				if (mr.Name == "set_text")
				{
					ins.OpCode = OpCodes.Call;
					ins.Operand = setText;
					sets++;
				}
				else if (mr.Name == "get_text")
				{
					ins.OpCode = OpCodes.Call;
					ins.Operand = getText;
					gets++;
				}
			}
		}
	}
}
Console.WriteLine($"hooked {sets} TextMesh.text setters, {gets} getters");

// Key prompts are the only caller. Show the count as digits so the
// translation can say 你有3个 instead of turning "one" into 一.
var intToWords = module.GetType("Gmath").Methods.Single(m => m.Name == "IntToWords");
intToWords.Body.Instructions.Clear();
intToWords.Body.ExceptionHandlers.Clear();
intToWords.Body.Variables.Clear();
var toString = module.ImportReference(new MethodReference("ToString", module.TypeSystem.String, module.TypeSystem.Int32) { HasThis = true });
var words = intToWords.Body.GetILProcessor();
// Int32.ToString is an instance method, so the number has to be passed by address.
// ldarg.0 pushes the value and the call faults, which aborts the door prompt.
words.Emit(OpCodes.Ldarga, intToWords.Parameters[0]);
words.Emit(OpCodes.Call, toString);
words.Emit(OpCodes.Ret);
Console.WriteLine("rewrote Gmath.IntToWords");

// Opening the stronghold inventory destroys the HUD panel, then a later turn
// refresh turns the exit button back on. Leaving from that button starts the
// level exit against the destroyed panel and never returns control of the party.
var mapExplore = module.GetType("MapExplore");
var inventoryOpen = mapExplore.Fields.Single(f => f.Name == "inventoryManage");
var baseOpen = mapExplore.Fields.Single(f => f.Name == "baseManage");
var leaveArea = mapExplore.Methods.Single(m => m.Name == "ButtonHandler_LeaveArea");
var leaveIl = leaveArea.Body.GetILProcessor();
var leaveRet = leaveIl.Create(OpCodes.Ret);
leaveIl.Append(leaveRet);
var leaveHead = leaveArea.Body.Instructions[0];
leaveIl.InsertBefore(leaveHead, leaveIl.Create(OpCodes.Ldarg_0));
leaveIl.InsertBefore(leaveHead, leaveIl.Create(OpCodes.Ldfld, inventoryOpen));
leaveIl.InsertBefore(leaveHead, leaveIl.Create(OpCodes.Ldarg_0));
leaveIl.InsertBefore(leaveHead, leaveIl.Create(OpCodes.Ldfld, baseOpen));
leaveIl.InsertBefore(leaveHead, leaveIl.Create(OpCodes.Or));
leaveIl.InsertBefore(leaveHead, leaveIl.Create(OpCodes.Brtrue, leaveRet));
Console.WriteLine("ignored leave-area while stronghold panels are open");

// Clicking Return to Stronghold while the arrival wipe is still running turns off
// clicks, then EnterLevel gives up because moving is not allowed yet. Nothing turns
// clicks back on, so only Escape still works. Give the click back on that exit.
var overworld = module.GetType("OverworldScript");
var clickAllowed = overworld.Fields.Single(f => f.Name == "clickAllowed");
var moveAllowed = overworld.Fields.Single(f => f.Name == "moveallowed");
var enterLevel = overworld.NestedTypes.Single(t => t.Name.Contains("<EnterLevel>")).Methods.Single(m => m.Name == "MoveNext");
var enterIns = enterLevel.Body.Instructions;
var moveCheck = enterIns.Single(i => i.OpCode == OpCodes.Ldfld && ((FieldReference)i.Operand).Name == moveAllowed.Name);
var bail = moveCheck.Next;
if (bail.OpCode != OpCodes.Brfalse)
{
	throw new Exception("EnterLevel: unexpected moveallowed check");
}
var enterIl = enterLevel.Body.GetILProcessor();
var thisField = enterLevel.DeclaringType.Fields.Single(f => f.Name == "<>f__this");
var exit = (Instruction)bail.Operand;
var restore = enterIl.Create(OpCodes.Ldarg_0);
enterIl.Append(restore);
enterIl.Append(enterIl.Create(OpCodes.Ldfld, thisField));
enterIl.Append(enterIl.Create(OpCodes.Ldc_I4_1));
enterIl.Append(enterIl.Create(OpCodes.Stfld, clickAllowed));
enterIl.Append(enterIl.Create(OpCodes.Br, exit));
bail.Operand = restore;
Console.WriteLine("restored world map clicks when entering is refused during the wipe");

// Literal replacements. TSV columns: type, original, replacement (\n escapes allowed).
var replacements = new Dictionary<(string, string), string>();
if (File.Exists(literalsPath))
{
	foreach (var line in File.ReadAllLines(literalsPath))
	{
		if (line.Length == 0 || line.StartsWith("#"))
		{
			continue;
		}
		var cols = line.Split('\t');
		if (cols.Length != 3)
		{
			throw new Exception("bad literals line: " + line);
		}
		replacements[(cols[0], Unescape(cols[1]))] = Unescape(cols[2]);
	}
}
var used = new HashSet<(string, string)>();
foreach (var type in module.GetTypes())
{
	foreach (var method in type.Methods.Where(m => m.HasBody))
	{
		foreach (var ins in method.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldstr))
		{
			string text = (string)ins.Operand;
			var key = (type.Name, text);
			var any = ("*", text);
			if (replacements.TryGetValue(key, out var value) || replacements.TryGetValue(any, out value))
			{
				ins.Operand = value;
				used.Add(key);
				used.Add(any);
			}
		}
	}
}
foreach (var key in replacements.Keys.Where(k => !used.Contains(k)))
{
	throw new Exception($"literal not found: {key.Item1} {key.Item2}");
}
Console.WriteLine($"replaced {used.Count} literals");

assembly.Write(outputPath);
Console.WriteLine("wrote " + outputPath);

static string Unescape(string s) => s.Replace("\\n", "\n").Replace("\\t", "\t");
