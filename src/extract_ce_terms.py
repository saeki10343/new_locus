import os
import javalang

def find_java_files(root):
    java_files = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".java"):
                java_files.append(os.path.join(dirpath, filename))
    return java_files

def extract_entities_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    try:
        tree = javalang.parse.parse(code)
    except Exception:
        return set()

    entities = set()
    if tree.package:
        entities.add(tree.package.name)

    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            entities.add(node.name)
        elif isinstance(node, javalang.tree.MethodDeclaration):
            entities.add(node.name)
        elif isinstance(node, javalang.tree.InterfaceDeclaration):
            entities.add(node.name)

    return entities

def extract_ce_vocab(source_root):
    all_entities = set()
    files = find_java_files(source_root)

    for filepath in files:
        ents = extract_entities_from_file(filepath)
        all_entities.update(ents)

    return sorted(all_entities)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str, required=True, help="Javaソースコードのルートディレクトリ（例：src）")
    parser.add_argument("--out", type=str, default="ce_vocab.txt", help="出力ファイル名")
    args = parser.parse_args()

    ce_terms = extract_ce_vocab(args.src)

    with open(args.out, 'w') as f:
        for term in ce_terms:
            f.write(term + '\n')

    print(f"✅ 抽出完了：{len(ce_terms)} 個のCE語彙 -> {args.out}")
