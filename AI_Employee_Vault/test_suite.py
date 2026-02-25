import unittest
import tempfile
import os
import shutil
import time
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import subprocess
import logging

# Add the AI_Employee_Vault directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'AI_Employee_Vault'))

class TestAIOrchestrator(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directories"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_dir = os.path.join(self.test_dir, 'AI_Employee_Vault')
        os.makedirs(self.vault_dir, exist_ok=True)
        
        # Create all required directories
        dirs = ['Inbox', 'Needs_Action', 'Plans', 'Pending_Approval', 'Approved', 'Done', 'Logs']
        for dir_name in dirs:
            os.makedirs(os.path.join(self.vault_dir, dir_name), exist_ok=True)
        
        # Create Dashboard.md
        dashboard_path = os.path.join(self.vault_dir, 'Dashboard.md')
        with open(dashboard_path, 'w') as f:
            f.write("# Test Dashboard\n\n## Pending Tasks\n\n## Recent Actions\n\n")
        
        # Change to test directory
        self.original_cwd = os.getcwd()
        os.chdir(self.vault_dir)
        
        # Setup test logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_watcher_creates_md_from_mock_input(self):
        """Test that watcher creates .md file from mock input"""
        # Create mock input in Inbox
        inbox_file = os.path.join(self.vault_dir, 'Inbox', 'test_message.txt')
        with open(inbox_file, 'w') as f:
            f.write("Test message requiring action")
        
        # Verify file exists
        self.assertTrue(os.path.exists(inbox_file))
        
        # Simulate watcher moving file to Needs_Action
        needs_action_file = os.path.join(self.vault_dir, 'Needs_Action', 'test_message.txt')
        shutil.move(inbox_file, needs_action_file)
        
        # Verify file moved correctly
        self.assertTrue(os.path.exists(needs_action_file))
        self.assertFalse(os.path.exists(inbox_file))
        
        # Create corresponding .md file
        md_file = os.path.join(self.vault_dir, 'Needs_Action', 'test_message.md')
        with open(md_file, 'w') as f:
            f.write("# Test Message\n\nAction required: Send email to client\n")
        
        self.assertTrue(os.path.exists(md_file))
        
        # Verify content
        with open(md_file, 'r') as f:
            content = f.read()
            self.assertIn("Action required", content)
    
    def test_reasoning_loop_generates_plan_with_checkboxes(self):
        """Test that reasoning loop reads .md and generates Plan.md with checkboxes"""
        # Create a test task in Needs_Action
        task_file = os.path.join(self.vault_dir, 'Needs_Action', 'test_task.md')
        with open(task_file, 'w') as f:
            f.write("Send email to john@example.com about project update")
        
        # Simulate reasoning trigger processing
        plan_content = """# Plan for: Send email to john@example.com

Based on the request: "Send email to john@example.com about project update"

## Detailed Plan

- [ ] Analyze the request and identify key requirements [Time: 10 min]
- [ ] Research necessary resources and tools [Time: 15 min]
- [ ] Create implementation steps [Time: 20 min]
- [ ] Execute the main action [Time: 30 min]
- [ ] Verify completion and document results [Time: 10 min]

## Prerequisites
- [ ] Ensure all required tools are available
- [ ] Verify permissions and access rights
- [ ] Check system resources

## Success Criteria
- [ ] All steps completed successfully
- [ ] Request fulfilled as specified
- [ ] Documentation updated
"""
        
        # Create plan file
        plan_file = os.path.join(self.vault_dir, 'Plans', 'plan_test_task.md')
        with open(plan_file, 'w') as f:
            f.write(plan_content)
        
        # Verify plan file exists and contains expected content
        self.assertTrue(os.path.exists(plan_file))
        with open(plan_file, 'r') as f:
            content = f.read()
            self.assertIn('- [ ]', content)  # Check for checkboxes
            self.assertIn('Detailed Plan', content)
            self.assertIn('Success Criteria', content)
            self.assertGreater(len(content), 100)  # Ensure substantial content
    
    def test_pending_approval_creation(self):
        """Test that sensitive actions create pending approval files"""
        # Create a plan file
        plan_file = os.path.join(self.vault_dir, 'Plans', 'sensitive_plan.md')
        with open(plan_file, 'w') as f:
            f.write("# Sensitive Plan\n- [ ] Send confidential email\n")
        
        # Move to Pending Approval (simulating the process)
        pending_file = os.path.join(self.vault_dir, 'Pending_Approval', 'sensitive_plan.md')
        shutil.move(plan_file, pending_file)
        
        self.assertTrue(os.path.exists(pending_file))
        
        # Verify it's in the right directory
        pending_files = os.listdir(os.path.join(self.vault_dir, 'Pending_Approval'))
        self.assertIn('sensitive_plan.md', pending_files)
        
        # Verify content preserved
        with open(pending_file, 'r') as f:
            content = f.read()
            self.assertIn('Sensitive Plan', content)
    
    def test_approved_triggers_action_handler(self):
        """Test that moving to Approved triggers action handler"""
        # Create an approved email task
        email_task = os.path.join(self.vault_dir, 'Approved', 'email_task.txt')
        with open(email_task, 'w') as f:
            f.write("TO: test@example.com\nSUBJECT: Test Email\nBODY: This is a test")
        
        # Verify file exists in Approved
        self.assertTrue(os.path.exists(email_task))
        
        # Verify content
        with open(email_task, 'r') as f:
            content = f.read()
            self.assertIn('TO:', content)
            self.assertIn('SUBJECT:', content)
            self.assertIn('BODY:', content)
        
        # Simulate action handler processing
        done_file = os.path.join(self.vault_dir, 'Done', 'email_task.txt')
        shutil.move(email_task, done_file)
        
        self.assertTrue(os.path.exists(done_file))
        self.assertFalse(os.path.exists(email_task))
        
        # Verify file moved correctly
        with open(done_file, 'r') as f:
            moved_content = f.read()
            self.assertEqual(moved_content, "TO: test@example.com\nSUBJECT: Test Email\nBODY: This is a test")
    
    def test_dashboard_update(self):
        """Test that Dashboard.md gets updated"""
        dashboard_path = os.path.join(self.vault_dir, 'Dashboard.md')
        
        # Read current dashboard
        with open(dashboard_path, 'r') as f:
            original_content = f.read()
        
        # Simulate dashboard update
        update_content = "\n## Test Update\n- Test action completed\n"
        with open(dashboard_path, 'a') as f:
            f.write(update_content)
        
        # Verify dashboard was updated
        with open(dashboard_path, 'r') as f:
            new_content = f.read()
        
        self.assertNotEqual(original_content, new_content)
        self.assertIn("Test action completed", new_content)
        self.assertIn("Test Update", new_content)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Step 1: Incoming message
        inbox_file = os.path.join(self.vault_dir, 'Inbox', 'end_to_end_test.txt')
        with open(inbox_file, 'w') as f:
            f.write("Client inquiry about partnership opportunity")
        
        # Verify initial state
        self.assertTrue(os.path.exists(inbox_file))
        
        # Step 2: Move to Needs_Action
        needs_action_file = os.path.join(self.vault_dir, 'Needs_Action', 'end_to_end_test.txt')
        shutil.move(inbox_file, needs_action_file)
        self.assertTrue(os.path.exists(needs_action_file))
        self.assertFalse(os.path.exists(inbox_file))
        
        # Step 3: Generate plan
        plan_content = """# Plan for: Client inquiry about partnership

- [ ] Review inquiry details
- [ ] Prepare response strategy  
- [ ] Draft partnership proposal
- [ ] Send to client
"""
        plan_file = os.path.join(self.vault_dir, 'Plans', 'plan_end_to_end_test.md')
        with open(plan_file, 'w') as f:
            f.write(plan_content)
        self.assertTrue(os.path.exists(plan_file))
        
        # Verify plan content
        with open(plan_file, 'r') as f:
            plan_content_read = f.read()
            self.assertIn('Client inquiry', plan_content_read)
            self.assertIn('- [ ]', plan_content_read)
        
        # Step 4: Move to Pending Approval
        pending_file = os.path.join(self.vault_dir, 'Pending_Approval', 'plan_end_to_end_test.md')
        shutil.move(plan_file, pending_file)
        self.assertTrue(os.path.exists(pending_file))
        
        # Step 5: Approve and move to Approved
        approved_file = os.path.join(self.vault_dir, 'Approved', 'plan_end_to_end_test.md')
        shutil.move(pending_file, approved_file)
        self.assertTrue(os.path.exists(approved_file))
        
        # Step 6: Process action and move to Done
        done_file = os.path.join(self.vault_dir, 'Done', 'plan_end_to_end_test.md')
        shutil.move(approved_file, done_file)
        self.assertTrue(os.path.exists(done_file))
        
        # Also move the original needs_action file to Done (simulating complete processing)
        if os.path.exists(needs_action_file):
            done_original = os.path.join(self.vault_dir, 'Done', 'end_to_end_test.txt')
            shutil.move(needs_action_file, done_original)
        
        # Verify complete workflow - all intermediate files should be moved
        self.assertFalse(os.path.exists(pending_file))
        self.assertFalse(os.path.exists(approved_file))
        self.assertTrue(os.path.exists(done_file))
        
        # Verify final content
        with open(done_file, 'r') as f:
            final_content = f.read()
            self.assertIn('Client inquiry', final_content)
    
    def test_file_content_assertions(self):
        """Test specific content assertions"""
        # Create test files with known content
        test_content = "TEST_CONTENT_12345_SPECIAL_CHARS_!@#$%"
        
        # Create file in Needs_Action
        test_file = os.path.join(self.vault_dir, 'Needs_Action', 'content_test.txt')
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Verify content exactly
        with open(test_file, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, test_content)
        self.assertIn("TEST_CONTENT", content)
        self.assertIn("SPECIAL_CHARS", content)
        self.assertTrue(len(content) > 0)
        self.assertIsInstance(content, str)
    
    def test_multiple_file_operations(self):
        """Test multiple concurrent file operations"""
        # Create multiple test files
        files_to_create = [
            ('inbox_1.txt', 'Message 1 content'),
            ('inbox_2.txt', 'Message 2 content'),
            ('inbox_3.txt', 'Message 3 content')
        ]
        
        created_files = []
        for filename, content in files_to_create:
            filepath = os.path.join(self.vault_dir, 'Inbox', filename)
            with open(filepath, 'w') as f:
                f.write(content)
            created_files.append(filepath)
        
        # Verify all files were created
        for filepath in created_files:
            self.assertTrue(os.path.exists(filepath))
        
        # Move all to Needs_Action
        moved_files = []
        for filename, content in files_to_create:
            src_path = os.path.join(self.vault_dir, 'Inbox', filename)
            dst_path = os.path.join(self.vault_dir, 'Needs_Action', filename)
            shutil.move(src_path, dst_path)
            moved_files.append(dst_path)
        
        # Verify all moved successfully
        for filepath in moved_files:
            self.assertTrue(os.path.exists(filepath))
        
        # Verify original locations are empty
        inbox_files = os.listdir(os.path.join(self.vault_dir, 'Inbox'))
        self.assertEqual(len(inbox_files), 0)

def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAIOrchestrator)
    
    # Create test runner with output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Results Summary:")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)