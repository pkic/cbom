-- Rewrites relative links to the tagged release on GitHub.
-- Links in the Markdown are written relative to publications/src/.
-- The tag is set by the build script through the CBOM_TAG variable.
local tag = os.getenv("CBOM_TAG") or "release-1"
local repo = "https://github.com/pkic/cbom/"

local function normalise(path)
  local parts = {}
  for part in ("publications/src/" .. path):gmatch("[^/]+") do
    if part == ".." then table.remove(parts)
    elseif part ~= "." then table.insert(parts, part) end
  end
  return table.concat(parts, "/")
end

function Link(el)
  local t = el.target
  if t:match("^%a[%w+.-]*:") or t:match("^#") or t:match("^mailto:") then
    return el
  end
  -- Folders use GitHub's tree view, files its blob view.
  local kind = t:match("/$") and "tree/" or "blob/"
  el.target = repo .. kind .. tag .. "/" .. normalise(t)
  return el
end
