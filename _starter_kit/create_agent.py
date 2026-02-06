#!/usr/bin/env python3
import os
import shutil
import re
import sys

def get_input(prompt, default=None):
    """Get input from user with an optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input

def replace_placeholders(content, replacements):
    """Replace all placeholders in the content with values from replacements dict."""
    for key, value in replacements.items():
        # Case insensitive replacement for {{KEY}}
        pattern = re.compile(re.escape("{{" + key + "}}"), re.IGNORECASE)
        content = pattern.sub(str(value), content)
    return content

def main():
    print("🚀 AI Agent Creator - Starter Kit Automation")
    print("============================================")
    
    # Base directory of the starter kit (where this script resides)
    kit_dir = os.path.dirname(os.path.abspath(__file__))
    structure_dir = os.path.join(kit_dir, "structure", "🧠_Agent_System")
    config_dir = os.path.join(kit_dir, "config")

    if not os.path.exists(structure_dir) or not os.path.exists(config_dir):
        print(f"❌ Error: Required directories not found in {kit_dir}")
        print("Ensure 'structure/🧠_Agent_System' and 'config' exist.")
        sys.exit(1)

    # 1. Collect Configuration
    print("\n📝 1. Configuration (Press Enter to accept defaults)")
    
    agent_name = get_input("Agent Name", "NewAgent")
    agent_emoji = get_input("Agent Emoji", "🤖")
    agent_type = get_input("Agent Type", "AI Assistant")
    agent_vibe = get_input("Agent Vibe", "Professional & Helpful")
    agent_tagline = get_input("Agent Tagline", "Here to serve.")
    user_name = get_input("User Name", "主人")
    primary_lang = get_input("Primary Language", "台灣繁體中文")
    project_a = get_input("Project Name (Optional)", "MyProject")

    # 2. Paths
    print("\n📂 2. Target Paths")
    current_dir = os.getcwd()
    target_vault_path = get_input("Target Vault Path (Where to create 🧠_Agent_System)", current_dir)
    target_vault_path = os.path.abspath(os.path.expanduser(target_vault_path))

    # Determine default config path (usually inside the agent system or a dedicated config folder)
    # Based on README, it says "Into your Agent config directory". 
    # Often this is 🧠_Agent_System/99_System or just the root of the profile.
    # We'll ask the user, default to 🧠_Agent_System/99_System/Config
    default_config_rel = os.path.join("🧠_Agent_System", "99_System", "Config")
    target_config_path_input = get_input("Target Config Directory (Relative to Vault or Absolute)", default_config_rel)
    
    if os.path.isabs(target_config_path_input):
        target_config_path = target_config_path_input
    else:
        target_config_path = os.path.join(target_vault_path, target_config_path_input)

    # Replacements Dictionary
    replacements = {
        "AGENT_NAME": agent_name,
        "AGENT_EMOJI": agent_emoji,
        "AGENT_TYPE": agent_type,
        "AGENT_VIBE": agent_vibe,
        "AGENT_TAGLINE": agent_tagline,
        "USER_NAME": user_name,
        "PRIMARY_LANGUAGE": primary_lang,
        "VAULT_PATH": target_vault_path,
        "AGENT_CONFIG_DIR": target_config_path,
        "PROJECT_A": project_a
    }

    # 3. Execution
    print(f"\n🚀 Ready to create agent '{agent_name}' at:\n   {target_vault_path}")
    print(f"   Config files will be in: {target_config_path}")
    if get_input("Proceed?", "y").lower() != "y":
        print("Aborted.")
        sys.exit(0)

    # Copy Structure
    target_system_root = os.path.join(target_vault_path, "🧠_Agent_System")
    
    if os.path.exists(target_system_root):
        print(f"⚠️  Warning: {target_system_root} already exists.")
        if get_input("Overwrite/Merge?", "n").lower() != "y":
            print("Skipping structure copy.")
        else:
            print("Copying structure...")
            shutil.copytree(structure_dir, target_system_root, dirs_exist_ok=True)
    else:
        print("Copying structure...")
        shutil.copytree(structure_dir, target_system_root)

    # Process Config Files
    if not os.path.exists(target_config_path):
        os.makedirs(target_config_path)

    print("Processing config templates...")
    template_files = [f for f in os.listdir(config_dir) if f.endswith(".template")]
    
    for template_file in template_files:
        src_path = os.path.join(config_dir, template_file)
        # Remove .template extension
        dest_filename = template_file[:-9]
        dest_path = os.path.join(target_config_path, dest_filename)
        
        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = replace_placeholders(content, replacements)
            
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Created {dest_filename}")
        except Exception as e:
            print(f"❌ Failed to process {template_file}: {e}")

    print("\n✨ Agent Creation Complete! ✨")
    print("Next Steps:")
    print("1. Set your startup rules to read MEMORY.md")
    print(f"2. Check {os.path.join(target_config_path, 'MEMORY.md')}")

if __name__ == "__main__":
    main()
