import os


def read_doc():
    path = os.path.join('output', 'specs', 'venture_capital_backend_feasibility.md')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def test_file_exists():
    path = os.path.join('output', 'specs', 'venture_capital_backend_feasibility.md')
    assert os.path.exists(path), f"Feasibility doc not found at {path}"


def test_required_sections_present():
    content = read_doc()
    required = [
        '1) Executive Summary',
        '3) API Surface',
        '4) DB Schema Sketch',
        '5) Infra Components',
        '6) Scalability Analysis & Bottlenecks',
        '7) Privacy & Compliance Blockers',
        '9) Effort Estimates',
        '11) Acceptance Criteria',
        '12) Deliverables & Timeline',
    ]
    missing = [h for h in required if h not in content]
    assert not missing, f"Missing required sections in feasibility doc: {missing}"


def test_not_template_placeholder():
    content = read_doc()
    placeholders = ['Backend Feasibility Template', '-- End of template --', 'Please populate']
    present = [p for p in placeholders if p in content]
    assert not present, f"Feasibility doc appears to still be a template / placeholder: {present}"


def test_contains_priority_p1():
    content = read_doc()
    assert 'Priority: P1' in content, 'Expected "Priority: P1" to be present in the doc (top-level priority)'
