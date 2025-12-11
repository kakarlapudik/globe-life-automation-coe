# Versioning and Release Guide

This document describes the versioning strategy and release process for the Pipeline Design Framework.

## Table of Contents

- [Versioning Strategy](#versioning-strategy)
- [Version Pinning](#version-pinning)
- [Release Process](#release-process)
- [Upgrade Guide](#upgrade-guide)
- [Backward Compatibility](#backward-compatibility)
- [Changelog](#changelog)

---

## Versioning Strategy

The Pipeline Design Framework follows [Semantic Versioning 2.0.0](https://semver.org/).

### Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Incompatible API changes or breaking changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Examples

- `1.0.0` - Initial release
- `1.1.0` - New feature added (backward compatible)
- `1.1.1` - Bug fix (backward compatible)
- `2.0.0` - Breaking change (not backward compatible)

### Version Tags

All releases are tagged in Git using annotated tags:

```bash
git tag -a v1.0.0 -m "Release v1.0.0: Initial framework release"
```

---

## Version Pinning

### Why Pin Versions?

Version pinning ensures:
- **Stability**: Your pipeline won't break from framework updates
- **Reproducibility**: Deployments are consistent across environments
- **Control**: You choose when to upgrade

### How to Pin Versions

#### Azure DevOps Repository Resources

```yaml
resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/tags/v1.2.0'  # Pin to specific version
```

#### Recommended Pinning Strategy

1. **Production**: Always pin to specific version
   ```yaml
   ref: 'refs/tags/v1.2.0'
   ```

2. **Staging**: Pin to minor version (get patches automatically)
   ```yaml
   ref: 'refs/heads/release/v1.2'
   ```

3. **Development**: Use latest (optional)
   ```yaml
   ref: 'refs/heads/main'
   ```

### Version Compatibility Matrix

| Framework Version | CDK Version | Node.js | Python | .NET |
|-------------------|-------------|---------|--------|------|
| 1.0.x             | 2.100.0+    | 18.x+   | 3.9+   | 6.0+ |
| 1.1.x             | 2.100.0+    | 18.x+   | 3.9+   | 6.0+ |
| 2.0.x             | 2.120.0+    | 20.x+   | 3.10+  | 8.0+ |

---

## Release Process

### 1. Prepare Release

#### Update Version Numbers

```bash
# Update version in documentation
sed -i 's/Version: 1.0.0/Version: 1.1.0/g' **/*.{ts,py,cs}

# Update CHANGELOG.md
vim CHANGELOG.md
```

#### Run Tests

```bash
# Run all tests
npm test  # TypeScript
pytest    # Python
dotnet test  # .NET

# Validate examples
cd examples/python-app && cdk synth
cd examples/typescript-app && cdk synth
cd examples/dotnet-app && cdk synth
```

#### Update Documentation

- Update README.md with new features
- Update CHANGELOG.md with changes
- Update version compatibility matrix
- Review all documentation for accuracy

### 2. Create Release Branch

```bash
# Create release branch
git checkout -b release/v1.1.0

# Commit version updates
git add .
git commit -m "Prepare release v1.1.0"

# Push release branch
git push origin release/v1.1.0
```

### 3. Create Git Tag

```bash
# Create annotated tag
git tag -a v1.1.0 -m "Release v1.1.0

New Features:
- Added TypeScript ApplicationStack template
- Enhanced error messages
- Improved documentation

Bug Fixes:
- Fixed qualifier length validation
- Corrected permissions boundary application

Breaking Changes:
- None
"

# Push tag
git push origin v1.1.0
```

### 4. Merge to Main

```bash
# Create pull request from release branch to main
# After approval, merge to main

git checkout main
git merge release/v1.1.0
git push origin main
```

### 5. Create Release Notes

Create release in Azure DevOps or Git hosting platform:

**Title**: Pipeline Design Framework v1.1.0

**Description**:
```markdown
## What's New

### Features
- Added TypeScript ApplicationStack template
- Enhanced error validation messages
- Improved troubleshooting documentation

### Bug Fixes
- Fixed qualifier length validation (#123)
- Corrected permissions boundary application (#124)

### Documentation
- Added versioning guide
- Updated troubleshooting guide
- Enhanced setup instructions

## Upgrade Instructions

See [Upgrade Guide](#upgrade-guide) for detailed instructions.

## Breaking Changes

None - this is a backward-compatible release.

## Compatibility

- CDK: 2.100.0+
- Node.js: 18.x+
- Python: 3.9+
- .NET: 6.0+
```

### 6. Notify Users

- Send email to framework users
- Post in Teams channel
- Update internal wiki
- Schedule training session (for major releases)

---

## Upgrade Guide

### Minor Version Upgrades (e.g., 1.0.0 → 1.1.0)

Minor upgrades are backward compatible and safe to apply.

#### Step 1: Update Version Reference

```yaml
# Before
resources:
  repositories:
    - repository: pipeline-framework
      ref: 'refs/tags/v1.0.0'

# After
resources:
  repositories:
    - repository: pipeline-framework
      ref: 'refs/tags/v1.1.0'
```

#### Step 2: Test in Development

```bash
# Synthesize stack
cdk synth

# Deploy to dev environment
cdk deploy --app "cdk.out" --require-approval never
```

#### Step 3: Validate

- Check CloudFormation events
- Verify resources created correctly
- Test pipeline execution
- Review logs

#### Step 4: Deploy to Production

```bash
# After successful dev testing
cdk deploy --app "cdk.out" --require-approval broadening
```

### Major Version Upgrades (e.g., 1.x → 2.0.0)

Major upgrades may contain breaking changes. Follow migration guide carefully.

#### Step 1: Review Migration Guide

Read `MIGRATION_v2.md` for breaking changes and migration steps.

#### Step 2: Update Dependencies

```bash
# Update CDK
npm install aws-cdk-lib@2.120.0

# Update Node.js (if required)
nvm install 20
nvm use 20
```

#### Step 3: Update Code

Follow migration guide to update:
- Stack props
- Construct IDs
- Configuration format
- Environment variables

#### Step 4: Test Thoroughly

```bash
# Test synthesis
cdk synth

# Test deployment in isolated environment
cdk deploy --app "cdk.out" --context env=test-migration
```

#### Step 5: Gradual Rollout

1. Deploy to development
2. Deploy to staging
3. Monitor for issues
4. Deploy to production

### Patch Version Upgrades (e.g., 1.1.0 → 1.1.1)

Patch upgrades are bug fixes only - safe to apply immediately.

```yaml
# Update version reference
ref: 'refs/tags/v1.1.1'
```

---

## Backward Compatibility

### Compatibility Promise

- **Minor versions**: 100% backward compatible
- **Patch versions**: 100% backward compatible
- **Major versions**: May contain breaking changes

### Deprecation Policy

When deprecating features:

1. **Announce**: Document in CHANGELOG and release notes
2. **Warn**: Add deprecation warnings in code
3. **Wait**: Maintain for at least 2 minor versions
4. **Remove**: Only in next major version

Example:
```typescript
// v1.1.0 - Deprecation warning
console.warn('DEPRECATED: oldMethod() will be removed in v2.0.0. Use newMethod() instead.');

// v1.2.0 - Still available with warning
// v1.3.0 - Still available with warning

// v2.0.0 - Removed
```

### Breaking Change Guidelines

Breaking changes are only allowed in major versions and must:

1. Be clearly documented in CHANGELOG
2. Include migration guide
3. Provide automated migration tools (when possible)
4. Be announced at least 1 month in advance

---

## Changelog

### Format

We follow [Keep a Changelog](https://keepachangelog.com/) format.

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features in development

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed

### Removed
- Features that were removed

### Fixed
- Bug fixes

### Security
- Security fixes

## [1.1.0] - 2024-01-21

### Added
- TypeScript ApplicationStack template
- .NET ApplicationStack template
- Comprehensive troubleshooting guide
- Versioning and release documentation

### Changed
- Enhanced error validation messages
- Improved documentation structure

### Fixed
- Qualifier length validation
- Permissions boundary application

## [1.0.0] - 2024-01-15

### Added
- Initial framework release
- Python PipelineStack template
- TypeScript PipelineStack template
- .NET PipelineStack template
- Python ApplicationStack template
- Azure Pipeline templates
- Basic documentation
- Example applications
```

---

## Release Checklist

Use this checklist for each release:

### Pre-Release

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Examples validated
- [ ] Migration guide written (major versions)
- [ ] Breaking changes documented

### Release

- [ ] Release branch created
- [ ] Git tag created
- [ ] Tag pushed to repository
- [ ] Release notes published
- [ ] Main branch updated

### Post-Release

- [ ] Users notified
- [ ] Teams channel updated
- [ ] Wiki updated
- [ ] Training scheduled (major releases)
- [ ] Feedback collected

---

## Version History

| Version | Release Date | Type | Highlights |
|---------|--------------|------|------------|
| 1.0.0   | 2024-01-15   | Major | Initial release |
| 1.1.0   | 2024-01-21   | Minor | Added ApplicationStack templates |
| 1.1.1   | 2024-01-22   | Patch | Bug fixes |

---

## Support Policy

### Active Support

- **Current major version**: Full support (bug fixes, features, security)
- **Previous major version**: Security fixes only for 6 months
- **Older versions**: No support

### End of Life (EOL)

Versions reach EOL 6 months after next major version release.

Example:
- v1.x.x released: 2024-01-15
- v2.0.0 released: 2024-07-15
- v1.x.x EOL: 2025-01-15 (6 months after v2.0.0)

---

## Questions?

For questions about versioning or releases:

- Email: devops@company.com
- Teams: #pipeline-framework
- Documentation: See README.md
