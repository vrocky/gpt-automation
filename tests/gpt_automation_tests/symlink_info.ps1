param (
    [Parameter(Mandatory=$true)]
    [string]$Path
)

# Get symlink information
$item = Get-Item $Path

# Check if it's a symbolic link
if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
    # Get detailed information
    $details = Get-ItemProperty -Path $Path
    Write-Output "Symlink type: $($details.LinkType)"
} else {
    Write-Output "Not a symbolic link"
}
