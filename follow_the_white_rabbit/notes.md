# Part 1

Use `dnSpy` to open `FollowWhiteRabbit_Data/Managed/Assembly-CSharp.dll` and patch `PlayerController.CheckFallDeath()` to do nothing.

Or using datamining:
- Extract using `uTinyRipper`
- `Assets/Texture2D/flag1.png`

Flag: `CSCG{data_mining_teleport_or_gravity_patch?}`

# Part 2

Intersting stuff:
- `UILoader` loads debug menus and has `FLAG` keybinding (doesn't work, maybe because of ghosting?)
- `PlayerControler` and `PlayerInput`: remove jumping conditions
- Extract files using `uTinyRipper`: Scene `FlagLand_Update`
- Opening the scene in Unity doesn't quite work
- Looking at the scene file we find `TextMeshPro` elements with text `Y`, `_` and with `PartialFlag2` that sets text to `and_datamining_scenes`
- Add keyboard shortcut to additively load `FlagLand_Update`

`dnSpy`: `PartialFlag2`

```c#
public class PartialFlag2 : MonoBehaviour {
	private void Start() {
		this.flagProbablyHardToGetStatically();
		TextMeshPro component = base.GetComponent<TextMeshPro>();
		string text = "aof\\`drfe`dbbjQ|st|vg";
		int num = 0;
		for (int i = 0; i < text.Length; i++)
		{
			TextMeshPro textMeshPro = component;
			textMeshPro.text += ((char)((int)text[i] ^ num)).ToString();
			num++;
		}
	}

	private void flagProbablyHardToGetStatically() {
		base.GetComponent<TextMeshPro>().text = "";
	}

	private void Update() {}
}
```

`Y_and_datamining_scenes`

text script guid: `3ddb35930c1572f4c90ae45f07020951`

```yaml
--- !u!1 &91
GameObject:
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  serializedVersion: 5
  m_Component:
  - component: {fileID: 536}
  m_Layer: 9
  m_Name: BuildingOfFlag2
  m_TagString: Untagged
  m_Icon: {fileID: 0}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1

--- !u!1 &166
GameObject:
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  serializedVersion: 5
  m_Component:
  - component: {fileID: 610}
  m_Layer: 9
  m_Name: PartialFlag2Display
  m_TagString: Untagged
  m_Icon: {fileID: 0}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1

--- !u!1 &216
GameObject:
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  serializedVersion: 5
  m_Component:
  - component: {fileID: 660}
  m_Layer: 9
  m_Name: RoomOfFlag2
  m_TagString: Untagged
  m_Icon: {fileID: 0}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
```

Flag: `CSCG{03ASY_teleport_and_datamining_scenes}`
